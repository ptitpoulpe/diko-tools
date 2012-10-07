#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scipt for checking the formal consistency of Diko
# author: Paul Bédaride <paul.bedaride@gmail.com>
# date: 30/09/2012

class DikoRelation(object):
    def __init__(self, diko, id, n1, n2, t, w):
        self.diko = diko
        self.id = id
        self.src_id = n1
        self.dst_id = n2
        self.type = t
        self.weight = w
        self.src = None
        self.dst = None

    def check(self):
      if self.src_id not in self.diko.nodes:
        print 'Relation %s has an invalid starting node id'%self.id
      if self.dst_id not in self.diko.nodes:
        print 'Relation %s has an invalid ending node id'%self.id

    def __str__(self):
        return str(self.rid)
