#!/usr/bin/env python

import sys


def gml_sub(blob):
    lines = []
    for line in blob.split('\n'):
        line = line.strip()
        lines.append(line)
    blob = "\n".join(lines)

    blob = blob.replace('\n\n', '\n')
    blob = blob.replace(']\n', '},\n')
    blob = blob.replace('[\n', '{')
    blob = blob.replace('\n{', '\n    {')
    for s in ['id', 'label', 'source', 'target', 'value']:
        blob = blob.replace(s, '"%s":' % s)
    blob = blob.replace('\n"', ', "')
    blob = blob.replace('\n}', '}')
    return blob.strip('\n')


def main(graphfile):
    with open(graphfile, 'r') as f:
        blob = f.read()
    blob = ''.join(blob.split('service')[1:])
    nodes = blob.split('edge')[0]
    edges = ''.join(blob.split('edge')[1:]).strip().rstrip(']')

    nodes = gml_sub(nodes)
    edges = gml_sub(edges)
    print('{\n  "nodes":[')
    print(nodes.rstrip(','))
    print('  ],\n  "edges":[')
    print('    ' + edges.rstrip(','))
    print('  ]\n}\n')


if __name__ == '__main__':
    main('./topology-1.graphml')
