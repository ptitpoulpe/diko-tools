#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scipt for checking the formal consistency of Diko
# author: Paul Bédaride <paul.bedaride@gmail.com>
# date: 30/09/2012

import re, sys

nodeRE = re.compile(r'''^
    eid=(?P<eid>\d+):  # entry id
    n="(?P<n>.*?)":    # name
    t=(?P<t>\d+):      # type
    w=(?P<w>\d+)       # weight
    (?::nf(?P<nf>.*))? # formated name
    \n$''', re.VERBOSE)
termSpecRE = re.compile(r'''^
    .*?                # name
    (?:>(\d+))+        # specs
    $''', re.VERBOSE)
chunkRE = re.compile(r'''^
    ::>(?P<a>\d+)      # type of chunk
    :(?P<b>\d+)        # base id
    >(?P<c>\d+)        # type of relation
    :(?P<d>\d+)        # destination id
    $''', re.VERBOSE)
questionRE = re.compile(r'''^
    ::>(?P<a>\d+)      # type of argument
    :(?P<b>\d+)        # argument id
    >(?P<c>\d+)        # type
    :(?P<d>\d+)        # predicate id
    >(?P<e>\d+)        # missing type
    $''', re.VERBOSE)
relationRE = re.compile(r'''^
    rid=(?P<rid>\d+):  # relation id
    n1=(?P<n1>\d+):    # starting node
    n2=(?P<n2>\d+):    # ending node
    t=(?P<t>\d+):      # type
    w=(?P<w>-?\d+)     # weight
    \n$''', re.VERBOSE)

nodes = {}
relations = []
with open(sys.argv[1]) as diko:
  # reading lines
  for line in diko.readlines():
    if line.startswith('//') or line=='\n':
      continue
    node = nodeRE.match(line)
    if node:
      nodes[node.group('eid')] = node.groupdict()
      continue
    relation = relationRE.match(line)
    if relation:
      relations.append(relation.groupdict())
      continue
    print "the line %s was not parsed"%repr(line)
  
  for relation in relations:
    if relation['n1'] not in nodes:
      print 'Relation %s has an invalid starting node id'%relation
    if relation['n2'] not in nodes:
      print 'Relation %s has an invalid ending node id'%relation

  for node in nodes.values():
    name = node['n']
    if '>' in name:
      chunk = chunkRE.match(name)
      question = questionRE.match(name)
      termSpec = termSpecRE.match(name)
      if chunk:
        if node['t'] != '8':
          print 'Node %s must be of type 8'%node
        if chunk.group('b') not in nodes:
          print 'Node %s has an invalid reference node id'%node
        if chunk.group('d') not in nodes:
          print 'Node %s has an invalid reference node id'%node
      elif question:
        if node['t'] != '9':
          print 'Node %s must be of type 9'%node
        if question.group('b') not in nodes:
          print 'Node %s has an invalid reference node id'%node
        if question.group('d') not in nodes:
          print 'Node %s has an invalid reference node id'%node
      elif termSpec:
        if any(eid not in nodes for eid in  name.split('>')[1:]):
          print 'Node %s has an invalid specification node id'%node
      else:
        print 'Node %s have not well formated'%node


