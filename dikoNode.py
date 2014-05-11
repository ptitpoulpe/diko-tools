#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scipt for checking the formal consistency of Diko
# author: Paul Bédaride <paul.bedaride@gmail.com>
# date: 30/09/2012
import re

nodes_type = {  0: "generic",
                1: "term",
                2: "acception",
                3: "definition",
                4: "pos",
                6: "concept",
                7: "hub",
                8: "chunk",
                9: "questions",
               18: "data",
               36: "data_pot",
              666: "AKI"}

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

class DikoNode(object):
    """ Diko Node """

    def __init__(self, diko, id, name, type, weight, formated_name):
        self.diko = diko
        self.id = id
        self.name = name
        self.type = type
        self.weight = weight
        self.formated_name = formated_name
        self.relations_from = []
        self.relations_to = []

    def check(self):
      if '>' in self.name:
        chunk = chunkRE.match(self.name)
        question = questionRE.match(self.name)
        termSpec = termSpecRE.match(self.name)
        if chunk:
          if self.type != 8:
            print 'Node %s must be of type 8'%self.eid
          if int(chunk.group('b')) not in self.diko.nodes:
            print 'Node %s has an invalid reference node id'%self.id
          if int(chunk.group('d')) not in self.diko.nodes:
            print 'Node %s has an invalid reference node id'%self.id
        elif question:
          if self.type != 9:
            print 'Node %s must be of type 9'%self.eid
          if int(question.group('b')) not in self.diko.nodes:
            print 'Node %s has an invalid reference node id'%self.id
          if int(question.group('d')) not in self.diko.nodes:
            print 'Node %s has an invalid reference node id'%self.id
        elif termSpec:
          if any(eid.isdigit() and int(eid) not in self.diko.nodes
                 for eid in self.name.split('>')[1:]):
            print 'Node %s has an invalid specification node id'%self.id
        else:
          print 'Node %s have not well formated'%self.id

    def __str__(self):
      res = []
      res.append("Node %s:"%nodes_type[self.type])
      res.append("  id: %s"%self.id)
      res.append("  name: %s"%self.name)
      res.append("  weight: %s\n"%self.weight)
      if self.formated_name:
        res.append("  formated name: %s\n"%self.formated_name)
      if self.relations_from:
        res.append("  relations from:")
        for relation in self.relations_from:
          res.append("    -%s:%s-> %s"%(relation.type,
                                        relation.weight,
                                        relation.dst.name))
      if self.relations_to:
        res.append("  relations to:")
        for relation in self.relations_to:
          res.append("    <-%s:%s- %s"%(relation.type,
                                        relation.weight,
                                        relation.src.name))
      return "\n".join(res)
