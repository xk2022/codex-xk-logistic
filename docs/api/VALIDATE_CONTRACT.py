"""Validate document schemas and synthetic fixtures; no HTTP, DB, or product code.

Usage: python docs/api/VALIDATE_CONTRACT.py --oas-schema /path/to/schema.yaml
Requires preinstalled PyYAML and jsonschema. Does not download or install packages.
"""

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


def contract_format_checker():
    checker = FormatChecker()

    @checker.checks('date-time', raises=(ValueError, OverflowError))
    def offset_datetime(value):
        if not isinstance(value, str):
            return True
        # The installed jsonschema has no optional RFC3339 dependency. Validate
        # this contract's explicit offset/date profile using the standard library.
        pattern = (r'\d{4}-\d{2}-\d{2}[Tt](?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d'
                   r'(?:\.\d{1,6})?(?:[Zz]|[+-](?:[01]\d|2[0-3]):[0-5]\d)')
        if not re.fullmatch(pattern, value):
            return False
        parsed = datetime.fromisoformat(value.upper().replace('Z', '+00:00'))
        return parsed.utcoffset() is not None

    return checker


def require(condition, message):
    if not condition:
        raise ValueError(message)


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def graph_errors(draft):
    errors = []
    items = draft.get('items', [])
    tasks = draft.get('tasks', [])
    item_refs = [i['clientRef'] for i in items]
    task_refs = [t['clientRef'] for t in tasks]
    for label, refs in [('item', item_refs), ('task', task_refs)]:
        if len(refs) != len(set(refs)):
            errors.append('duplicate_' + label + '_ref')
    sequences = [i['sequence'] for i in items if i.get('sequence') is not None]
    if len(sequences) != len(set(sequences)):
        errors.append('duplicate_sequence')
    for task in tasks:
        if task['itemRef'] not in item_refs:
            errors.append('missing_item')
        for ref in task.get('predecessorRefs', []):
            if ref not in task_refs:
                errors.append('missing_predecessor')
            if ref == task['clientRef']:
                errors.append('self_predecessor')
        start, end = task.get('plannedStartAt'), task.get('plannedEndAt')
        if start and end and datetime.fromisoformat(end) < datetime.fromisoformat(start):
            errors.append('reversed_time')
    by_ref = {t['clientRef']: t for t in tasks}
    visiting, visited = set(), set()

    def visit(ref):
        if ref in visiting:
            return True
        if ref in visited or ref not in by_ref:
            return False
        visiting.add(ref)
        if any(visit(p) for p in by_ref[ref].get('predecessorRefs', [])):
            return True
        visiting.remove(ref)
        visited.add(ref)
        return False

    if any(visit(ref) for ref in by_ref):
        errors.append('cycle')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oas-schema', type=Path, required=True)
    args = parser.parse_args()
    api = Path(__file__).resolve().parent
    root = api.parents[1]
    spec = yaml.safe_load((api / 'openapi.yaml').read_text())
    official = yaml.safe_load(args.oas_schema.read_text())
    require(official.get('$id') == 'https://spec.openapis.org/oas/3.1/schema/2022-10-07',
            'Unexpected official OAS document schema')
    Draft202012Validator(official).validate(spec)
    reference_count = 0
    for obj in objects(spec):
        if '$ref' not in obj:
            continue
        ref = obj['$ref']
        require(ref.startswith('#/'), 'No remote refs in this contract: ' + ref)
        node = spec
        for token in ref[2:].split('/'):
            node = node[token.replace('~1', '/').replace('~0', '~')]
        reference_count += 1
    schemas = json.loads(json.dumps(spec['components']['schemas']).replace(
        '#/components/schemas/', '#/$defs/'))
    validators = {}
    for name in schemas:
        document = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
                    '$defs': schemas, '$ref': '#/$defs/' + name}
        Draft202012Validator.check_schema(document)
        validators[name] = Draft202012Validator(document, format_checker=contract_format_checker())
    fixtures = json.loads((api / 'ORDER_DRAFT_CONTRACT_EXAMPLES.json').read_text())
    require(fixtures['metadata']['synthetic'] is True, 'Fixtures must be synthetic')
    require(fixtures['metadata']['runtime_validation'] == 'not_run', 'Runtime was not executed')
    ids = []
    for group, positive in [('schemaPositive', True), ('schemaNegative', False)]:
        for fixture in fixtures[group]:
            errors = list(validators[fixture['schema']].iter_errors(fixture['value']))
            require(bool(errors) != positive, fixture['id'] + ': ' + str(errors[:1]))
            ids.append(fixture['id'])
            if positive and fixture['schema'] == 'OrderEnvelope':
                order = fixture['value']['data']
                item_ids = {i['clientRef']: i['id'] for i in order['items']}
                task_ids = {t['clientRef']: t['id'] for t in order['tasks']}
                for task in order['tasks']:
                    require(task['orderId'] == order['id'], fixture['id'] + ': wrong order')
                    require(item_ids[task['itemRef']] == task['itemId'], fixture['id'] + ': wrong item')
                    require([task_ids[r] for r in task['predecessorRefs']] == task['predecessorTaskIds'],
                            fixture['id'] + ': wrong predecessor IDs')
    for fixture in fixtures['graphCases']:
        validators['CreateDraftRequest'].validate(fixture['draft'])
        actual = graph_errors(fixture['draft'])
        require(bool(actual) == (fixture['expected'] == 'invalid_graph'), fixture['id'] + ': ' + str(actual))
        ids.append(fixture['id'])
    require(len(ids) == len(set(ids)), 'Duplicate fixture IDs')
    require(all(s['status'] == 'not_run' for s in fixtures['serviceScenariosNotRun']), 'Service was not run')
    operations = []
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if method not in {'get', 'put', 'post', 'delete', 'patch'}:
                continue
            operations.append(operation['operationId'])
            require(operation.get('x-implementation-status') == 'not_implemented', 'No runtime claim')
            require(operation.get('security', spec.get('security')) == [{'sessionAuth': []}], 'Session required')
            params = [p.get('$ref', '') for p in operation.get('parameters', [])]
            if method in {'post', 'put'}:
                require('#/components/parameters/CsrfToken' in params, 'CSRF header required')
                require('#/components/parameters/IdempotencyKey' in params, 'Idempotency required')
            if '{orderId}' in path:
                require('#/components/parameters/OrderId' in params, 'Path UUID required')
    require(len(operations) == len(set(operations)) == 5, 'Expected five unique operations')
    policy_document = json.loads((api / 'ORDER_DRAFT_ACCESS_POLICY.json').read_text())
    require(policy_document['contractVersion'] == spec['info']['version'] == '0.2.0',
            'Authorization document version must match OpenAPI')
    require(policy_document['status'] == 'accepted_not_implemented', 'Policy is a contract, not runtime evidence')
    require(policy_document['runtime_validation'] == 'not_run', 'Authorization HTTP checks were not run')
    require(policy_document['decisionIds'] == ['ACC-P01', 'ACC-P02'], 'Only adopted access decisions')
    require(policy_document['multiRoleResolution'] == 'pending_START-P03', 'Multiple-role policy remains pending')
    bindings = policy_document['bindings']
    require(len(bindings) == 15, 'Expected five operations by three single roles')
    actual_bindings = {(b['operationId'], b['singleLogicalRole']): b for b in bindings}
    require(len(actual_bindings) == 15, 'Duplicate authorization binding')
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if method not in {'get', 'put', 'post'}:
                continue
            policy = operation['x-authorization-policy']
            require(policy['status'] == 'accepted_not_implemented', 'Adopted scope required')
            require(policy['companyScope'] == policy_document['scope'] == 'server_current_company',
                    'Client cannot choose company scope')
            require(policy['allowedSingleRoles'] == ['ADMIN', 'DISPATCHER'], 'Adopted manager/dispatcher scope')
            require(policy['deniedSingleRoles'] == ['DRIVER'], 'Driver cannot use aggregate API')
            require(policy['authorizationBeforeIdempotencyReplay'] is True, 'Replay must reauthorize')
            for role in ['ADMIN', 'DISPATCHER', 'DRIVER']:
                binding = actual_bindings[(operation['operationId'], role)]
                require(binding['path'] == path and binding['method'] == method.upper(), 'Binding route mismatch')
                require(binding['access'] == ('DENY_403' if role == 'DRIVER' else 'ALLOW_WITH_SCOPE_AND_GUARDS'),
                        'Binding contradicts adopted role scope')
            require('403' in operation['responses'], 'No-role response must be documented')
    with (root / 'docs/FIRST_SLICE_ORDER_FIELDS.csv').open() as file:
        rows = list(csv.DictReader(file))
    require(len(rows) == len({r['id'] for r in rows}) == 40, 'Expected 40 unique business definitions')
    require(all(r['status'] != 'PROPOSED' and r['accepted_scope'] and r['pending_scope'] for r in rows),
            'Adoption and pending scopes required')
    markdown_count, link_count = 0, 0
    for path in root.rglob('*.md'):
        text = path.read_text()
        require(len(re.findall(r'^```', text, re.M)) % 2 == 0, str(path) + ': unbalanced fence')
        require(not re.search(r'^(<<<<<<<|=======|>>>>>>>)', text, re.M), str(path) + ': conflict marker')
        require(not re.search(r'[\t ]+$', text, re.M) or path.name != 'CHANGELOG.md', 'Changelog trailing space')
        for target in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)', text):
            if target.startswith(('http:', 'https:', 'mailto:', '#')):
                continue
            require((path.parent / target.split('#')[0]).exists(), str(path) + ': missing link ' + target)
            link_count += 1
        markdown_count += 1
    print(json.dumps({
        'oasDocumentShape': 'pass (official OAI 2022-10-07 schema; components validated separately)',
        'componentSchemas': len(schemas), 'internalRefs': reference_count, 'operations': len(operations),
        'authorizationDocumentBindings': len(bindings),
        'schemaPositive': len(fixtures['schemaPositive']), 'schemaNegative': len(fixtures['schemaNegative']),
        'graphCases': len(fixtures['graphCases']), 'businessFieldDefinitions': len(rows),
        'markdownFiles': markdown_count, 'localLinks': link_count,
        'serviceScenariosNotRun': len(fixtures['serviceScenariosNotRun']),
        'runtime': 'NOT RUN: product build, DB, HTTP, auth/CSRF, concurrency, deployment',
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
