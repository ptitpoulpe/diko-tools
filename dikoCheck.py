#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scipt for checking the formal consistency of Diko
# author: Paul Bédaride <paul.bedaride@gmail.com>
# date: 30/09/2012
#
# eid=336:n="Astrakhan":t=1:w=50
# rid=133275:n1=141480:n2=18280:t=10:w=50
#
# eid=336|n="Astrakhan"|t=1|w=50
# rid=133275|n1=141480|n2=18280|t=10|w=50

import re, sys, codecs
import sqlite3

nodeRE = re.compile(r'''^
    eid=(?P<eid>\d+)\| # entry id
    n="(?P<n>.*?)"\|   # name
    t=(?P<t>\d+)\|     # type
    w=(?P<w>\d+)       # weight
    (?:\|nf(?P<nf>.*))? # formated name
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
    rid=(?P<rid>\d+)\| # relation id
    n1=(?P<n1>\d+)\|   # starting node
    n2=(?P<n2>\d+)\|   # ending node
    t=(?P<t>\d+)\|     # type
    w=(?P<w>-?\d+)     # weight
    \n$''', re.VERBOSE)
relationTypeRE = re.compile(r'''^
    rtid=(?P<rtid>\d+)\|                  # relation type id
    name="(?P<name>.*?)"\|                # relation type name
    nom_etendu="(?P<extended_name>.*?)"\| # relation type extended name
    info="(?P<info>.*?)"                  # relation type info
    \n$''', re.VERBOSE)

class Diko(object):
  def __init__(self, sqlite, xml=None):
    self.conn = sqlite3.connect(sqlite)
    self.conn.text_factory = str
    self.c = self.conn.cursor()

    self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    if xml is not None and len(self.c.fetchall())==0:
      self.createDatabase()
      self.fillDatabase(xml)

  def __del__(self):
    self.conn.close()

  def createDatabase(self):
    self.c.executescript('''
CREATE TABLE nodes(
  id integer PRIMARY KEY,
  name text,
  type integer,
  weight integer, 
  formated_name text);

CREATE TABLE relations(
  id integer PRIMARY KEY ,
  src integer,
  dst integer,
  type integer,
  weight integer);

CREATE TABLE chunks(
  id integer PRIMARY KEY,
  type integer,
  base integer,
  relation integer,
  dest integer);

CREATE TABLE questions(
  id integer PRIMARY KEY,
  argument_type integer,
  argument_id integer,
  question_type integer,
  pred_id integer,
  missing_type integer);

CREATE TABLE terms(
  id integer,
  place integer,
  term integer,
  PRIMARY KEY (id, place));
''')

  def fillDatabase(self, xml):
    with codecs.open(xml) as diko:
      # reading lines
      for line in diko:
        if line.startswith('//') or line=='\n':
          continue
        node = nodeRE.match(line)
        if node:
          name = node.group('n')
          nid = int(node.group('eid'))
          if '>' in name:
            chunk = chunkRE.match(name)
            if chunk:
              self.c.execute(u"INSERT INTO chunks VALUES (?,?,?,?,?)",
                        (nid,
                         int(chunk.group('a')),
                         int(chunk.group('b')),
                         int(chunk.group('c')),
                         int(chunk.group('d'))))
              name = ''
              pass
            
            question = questionRE.match(name)
            if question:
              self.c.execute(u"INSERT INTO questions VALUES (?,?,?,?,?,?)",
                        (nid,
                         int(question.group('a')),
                         int(question.group('b')),
                         int(question.group('c')),
                         int(question.group('d')),
                         int(question.group('e'))))
              name = ''
              pass
      
            termSpec = termSpecRE.match(name)
            if termSpec:
              self.c.executemany("INSERT INTO terms VALUES (?,?,?)",
                            [(nid, i, int(id)) for i,id in enumerate(name.split('>')[1:])])
              name = ''
          self.c.execute(u"INSERT INTO nodes VALUES (?,?,?,?,?)",
                    (nid,
                     name,
                     int(node.group('t')),
                     int(node.group('w')),
                     node.group('nf')))
          continue
        relation = relationRE.match(line)
        if relation:
          self.c.execute(u"INSERT INTO relations VALUES (?,?,?,?,?)",
                    (int(relation.group('rid')),
                     int(relation.group('n1')),
                     int(relation.group('n2')),
                     int(relation.group('t')),
                     int(relation.group('w'))))
          continue
        relationType = relationTypeRE.match(line)
        if relationType:
          continue
        print "the line %s was not parsed"%repr(line)
      
      self.conn.commit()
   
  def nodes(self, word):
    return [Node(self, *node) for node in self.c.execute(u"""SELECT * FROM nodes
               WHERE ? = name """, (word,)).fetchall()]

  def check(self):
    print "Checking relations src:"
    r = self.c.execute(u"""SELECT id, src FROM relations
                WHERE src NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking relations dst:"
    r = self.c.execute(u"""SELECT id, dst FROM relations
                WHERE dst NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking chunks type:"
    r = self.c.execute(u"""SELECT nodes.id, nodes.type
                FROM chunks
                JOIN nodes ON nodes.id = chunks.id
                WHERE nodes.type != 8""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking chunks base:"
    r = self.c.execute(u"""SELECT id, base FROM chunks
                WHERE base NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking chunks dest:"
    r = self.c.execute(u"""SELECT id, dest FROM chunks
                WHERE dest NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r
   
    print "Checking questions type:"
    r = self.c.execute(u"""SELECT nodes.id, nodes.type
                FROM questions
                JOIN nodes ON nodes.id = questions.id
                WHERE nodes.type != 9""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking questions pred:"
    r = self.c.execute(u"""SELECT id, pred_id FROM questions
                WHERE pred_id NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking questions argument:"
    r = self.c.execute(u"""SELECT id, argument_id FROM questions
                WHERE argument_id NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

    print "Checking terms:"
    r = self.c.execute(u"""SELECT * FROM terms
                WHERE term NOT IN (SELECT id FROM nodes)""").fetchall()
    print " ", "OK" if len(r)==0 else r

class Node(object):
  types = {0: "generic",
           1: "term", 
           2: "acception",
           3: "definition",
           4: "POS",
           5: "concept",
           6: "flpot",
           7: "hub",
           8: "chunk",
           9: "question",
           10: "relation",
           18: "data",
           36: "data_pot",
           666: "AKI",
           777: "wikipedia"}
  def __init__(self, diko, id, name, type, weight, formated_name):
    self.diko = diko
    self.id = id
    self.name = name
    self.type = self.types[type]
    self.weight = weight
    self.formated_name = formated_name

  def relationsFrom(self):
    return self.diko.c.execute(u"""SELECT * FROM relations
                WHERE src = ?""", (self.id,)).fetchall()

if __name__=="__main__":
  diko = Diko("diko.db", sys.argv[1])
  #diko.check()
  table = diko.nodes("table")[0]
  print table.type
  print table.relationsFrom()
