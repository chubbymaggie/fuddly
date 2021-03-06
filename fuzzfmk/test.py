################################################################################
#
#  Copyright 2014-2015 Eric Lacombe <eric.lacombe@security-labs.org>
#
################################################################################
#
#  This file is part of fuddly.
#
#  fuddly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  fuddly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with fuddly. If not, see <http://www.gnu.org/licenses/>
#
################################################################################

from __future__ import print_function

import sys
import copy
import re
import functools
import binascii
import unittest
import collections

import argparse

import json, collections

sys.path.append('.')

from fuzzfmk.data_model import *
from fuzzfmk.value_types import *

from libs.external_modules import *

import data_models.example as example
import data_models.protocols.usb

from fuzzfmk.fuzzing_primitives import *
from fuzzfmk.basic_primitives import *
from fuzzfmk.plumbing import *
from fuzzfmk.target import *
from fuzzfmk.logger import *

from fuzzfmk.data_model_helpers import *


parser = argparse.ArgumentParser(description='Process arguments.')
parser.add_argument('-a', '--all', action='store_true',
                    help='Run all test cases. Some can take lot of time. (Disabled by default.)')
parser.add_argument('--ignore-dm-specifics', action='store_true',
                    help='Run Data Models specific test cases. (Enabled by default.)')

test_args = parser.parse_known_args()
run_long_tests = test_args[0].all
ignore_data_model_specifics = test_args[0].ignore_dm_specifics

class TEST_Fuzzy_INT16(Fuzzy_INT16):
    int_list = ['TEST_OK', 'BLABLA', 'PLOP']
    
    def __init__(self, endian=None, supp_list=None):
        self.endian = endian
        self.idx = 0
        INT.__init__(self, int_list=self.int_list, determinist=True)

    def is_compatible(self, integer):
        return False

    def _convert_value(self, val):
        return val



######## Tests cases begins Here ########

# Legacy --> Need to be revamped
class TestBasics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dm = example.data_model
        cls.dm.load_data_model(fuzzer._name2dm)

    def setUp(self):
        pass

    def test_01(self):

        print('\n### TEST 0: generate one EX1 ###')

        node_ex1 = dm.get_data('EX1')

        print('Flatten 1: ', repr(node_ex1.get_flatten_value()))
        print('Flatten 1: ', repr(node_ex1.get_flatten_value()))
        l = node_ex1.get_value()
        hk = set(node_ex1.get_all_paths().keys())
        print(l)

        print('\n\n ####### \n\n')

        print(l[0])
        print(b' @ ' + b''.join(flatten(l[1])) + b' @ ')
        print(l[1])

        print('\n\n ####### \n\n')


        res1 = b' @ ' + b''.join(flatten(l[1])) + b' @ ' == l[0]
        print('*** Is the concatenation (first list element) correct? %r' % res1)

        res2 = len(b''.join(flatten(l[1]))) == int(l[2])
        print('*** Is length of the concatenation correct? %r' % res2)

        results['test0'] = res1 and res2

        print('\n### TEST 1: cross check self.node.get_all_paths().keys() and get_nodes_names() ###')

        print('*** Hkeys from self.node.get_all_paths().keys():')
        hk = sorted(hk)
        for k in hk:
            print(k)

        print('*** Hkeys from get_nodes_names():')
        l = sorted(node_ex1.get_nodes_names())
        for k in l:
            print(k)

        res1 = len(hk) == len(l)

        res2 = False
        for i in range(len(hk)):
            if hk[i] != l[i][0]:
                res2 = False
                break
        else:
            res2 = True

        results['test1'] = res1 and res2


        print('\n### TEST 2: generate two different EX1 ###')

        node_ex1.unfreeze()
        print(node_ex1.get_value())
        val1 = node_ex1.get_flatten_value()

        node_ex1.unfreeze()
        print(node_ex1.get_value())
        val2 = node_ex1.get_flatten_value()

        results['test2'] = val1 != val2


        print('\n### TEST 3: generate 4 identical TUX (with last one flatten) ###')

        tux = dm.get_data('TUX')

        val1 = tux.get_value()
        print(val1)
        val2 = tux.get_value()
        print(val2)
        val3 = tux.get_value()
        print(val3)

        print(repr(tux.get_flatten_value()))

        res = val1 == val2 and val1 == val3
        results['test3'] = res


        print('\n### TEST 4: generate 2 different flatten TUX ###')

        tux.unfreeze()
        val1 = repr(tux.get_flatten_value())
        print(val1)
        tux.unfreeze()
        val2 = repr(tux.get_flatten_value())
        print(val2)

        res = val1 != val2
        results['test4'] = res


        print('\n### TEST 5: test get_node_by_path() ###')

        print('\n*** test 5.1: get_node_by_path() with exact path')

        tux2 = dm.get_data('TUX')

        print('* Shall return None:')
        val1 = tux2.get_node_by_path(path='EX1')
        val2 = tux2.get_node_by_path(path='CONCAT')
        print(val1)
        print(val2)

        print('* Shall not return None:')
        val3 = tux2.get_node_by_path('TUX/TX')
        val4 = tux2.get_node_by_path('TUX/TC')
        print(val3)
        print(val4)

        res1 = val1 == None and val2 == None and val3 != None and val4 != None

        print('\n*** test 5.2: call 3 times get_node_by_path()')

        print('name: %s, result: %s' % ('TUX', tux2.get_node_by_path('TUX').get_path_from(tux2)))
        print('name: %s, result: %s' % ('TX', tux2.get_node_by_path('TX').get_path_from(tux2)))
        print('name: %s, result: %s' % ('KU', tux2.get_node_by_path('KU', conf='ALT').get_path_from(tux2)))
        print('name: %s, result: %s' % ('MARK3', tux2.get_node_by_path('MARK3', conf='ALT').get_path_from(tux2, conf='ALT')))

        print('\n*** test 5.3: call get_node_by_path() with real regexp')

        print('--> ' + tux2.get_node_by_path('TX.*KU').get_path_from(tux2))

        print('\n*** test 5.4: call get_reachable_nodes()')

        node_ex1 = dm.get_data('EX1')
        l = node_ex1.get_reachable_nodes(path_regexp='TUX')
        for i in l:
            print(i.get_path_from(node_ex1))

        print('\n')

        node_ex1 = dm.get_data('EX1')
        l = node_ex1.get_reachable_nodes(path_regexp='T[XC]/KU')
        for i in l:
            print(i.get_path_from(node_ex1))

        if len(l) == 4:
            res2 = True
        else:
            res2 = False

        print(res1, res2)

        results['test5'] = res1 and res2

        print('\n### TEST 6: get_reachable_nodes()')

        for e in sorted(tux2.get_nodes_names()):
            print(e)

        c1 = NodeInternalsCriteria(mandatory_attrs=[NodeInternals.Mutable],
                                  node_kinds=[NodeInternals_TypedValue])

        c2 = NodeInternalsCriteria(node_kinds=[NodeInternals_TypedValue])

        print('\n*** test 6.1:')

        l1 = tux2.get_reachable_nodes(internals_criteria=c1)

        l2 = tux2.get_reachable_nodes(internals_criteria=c2)

        res61 = len(l2) > len(l1)

        print('len(l1): %d, len(l2): %d' % (len(l1), len(l2)))

        print('\n*** test 6.2:')

        res62 = False
        l = tux2.get_reachable_nodes(internals_criteria=c2, conf='ALT')
        for k in l:
            print(k.get_path_from(tux2, conf='ALT'))
            if 'MARK3' in k.get_path_from(tux2, conf='ALT'):
                res62 = True
                break

        # l = tux2.get_reachable_nodes(node_kinds=[NodeInternals_NonTerm], conf='ALT')
        # for k in l:
        #     print(k.get_path_from(tux2, conf='ALT'))

        print('\n*** test 6.3:')

        c3 = NodeInternalsCriteria(node_kinds=[NodeInternals_Func])

        l3 = node_ex1.get_reachable_nodes(internals_criteria=c3)
        print("*** %d Func Node found" % len(l3))
        print(l3)

        res63 = len(l3) == 2

        print(res61, res62, res63)

        results['test6'] = res61 and res62 and res63

        print('\n### TEST 7: get_reachable_nodes() and change_subnodes_csts()')

        print('*** junk test:')

        tux2.get_node_by_path('TUX$').cc.change_subnodes_csts([('u=+', 'u>'), ('u=.', 'u>')])
        print(tux2.get_flatten_value())

        print('\n*** test 7.1:')

        print('> l1:')

        tux2 = dm.get_data('TUX')
        # attr = Elt_Attributes(defaults=False)
        # attr.conform_to_nonterm_node()

        # node_kind = [NodeInternals_NonTerm]

        crit = NodeInternalsCriteria(node_kinds=[NodeInternals_NonTerm])

        l1 = tux2.get_reachable_nodes(internals_criteria=crit)

        # tux2.cc.get_subnodes_csts_copy()
        # exit()

        res1 = True
        for e in l1:
            print(e.get_path_from(tux2))
            e.cc.change_subnodes_csts([('*', 'u=.')])
            csts1 = e.cc.get_subnodes_csts_copy()
            print(csts1)

            e.cc.change_subnodes_csts([('*', 'u=.'), ('u=.', 'u>')])
            csts2 = e.cc.get_subnodes_csts_copy()
            print(csts2)

            print('\n')

    #        val = cmp(csts1, csts2)
            val = (csts1 > csts2) - (csts1 < csts2)
            if val != 0:
                res1 = False


        print('> l2:')

        l2 = tux2.get_reachable_nodes(internals_criteria=crit)
        for e in l2:
            print(e.get_path_from(tux2))


        print('\n*** test 7.2:')

        res2 = len(l2) == len(l1)
        print('len(l2) == len(l1)? %r' % res2)


        print('\n*** test 7.3:')

        tux = dm.get_data('TUX')
        l1 = tux.get_reachable_nodes(internals_criteria=crit)
        c_l1 = []
        for e in l1:
            orig = e.cc.get_subnodes_csts_copy()

            e.cc.change_subnodes_csts([('u=.', 'u>'), ('u>', 'u=.')])
            csts1 = e.cc.get_subnodes_csts_copy()
            print(csts1)
            print('\n')
            c_l1.append(csts1)

            e.set_subnodes_full_format(orig)

        l2 = tux.get_reachable_nodes(internals_criteria=crit)
        c_l2 = []
        for e in l2:
            orig = e.cc.get_subnodes_csts_copy()

            e.cc.change_subnodes_csts([('u>', 'u=.'), ('u=.', 'u>')])
            csts2 = e.cc.get_subnodes_csts_copy()
            print(csts2)
            print('\n')
            c_l2.append(csts2)

        zip_l = zip(c_l1, c_l2)


        test = 1
        for zl1, zl2 in zip_l:

            for ze1, ze2 in zip(zl1, zl2):
                test = (ze1 > ze2) - (ze1 < ze2)
                if test != 0:
                    print(ze1)
                    print('########')
                    print(ze2)
                    print('########')
                    break

        if test != 0:
            res3 = False
        else:
            res3 = True


    #    val = cmp(c_l1, c_l2)
        val = (c_l1 > c_l2) - (c_l1 < c_l2)
        if val != 0:
            res3 = False
        else:
            res3 = True


        print(res1, res2, res3)

        results['test7'] = res1 and res2 and res3


        print('\n### TEST 8: set_current_conf()')

        node_ex1 = dm.get_data('EX1')

        print('\n*** test 8.0:')

        res01 = True
        l = sorted(node_ex1.get_nodes_names())
        for k in l:
            print(k)
            if 'EX1' != k[0][:len('EX1')]:
                res01 = False
                break

        l2 = sorted(node_ex1.get_nodes_names(conf='ALT'))
        for k in l2:
            print(k)
            if 'EX1' != k[0][:len('EX1')]:
                res01 = False
                break

        res02 = False
        for k in l2:
            if 'MARK2' in k[0]:
                for k in l2:
                    if 'MARK3' in k[0]:
                        res02 = True
                        break
                break

        res0 = res01 and res02

        print('\n*** test 8.1:')

        res1 = True

        msg = node_ex1.get_flatten_value(conf='ALT')
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg:
            res1 = False
        print(msg)
        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg:
            res1 = False
        print(msg)
        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value()
        if b' ~(..)~ ' in msg or b' ~(X)~ ' in msg:
            res1 = False
        print(msg)
        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg:
            res1 = False
        print(msg)
        node_ex1.unfreeze_all()


        print('\n*** test 8.2:')

        print('\n***** test 8.2.0: subparts:')

        node_ex1 = dm.get_data('EX1')

        res2 = True

        print(node_ex1.get_flatten_value())

        node_ex1.set_current_conf('ALT', root_regexp=None)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value()
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg or b'[<]' not in msg or b'[\xc2]' not in msg:
            res2 = False
        print(msg)
        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value()
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg or b'[<]' not in msg or b'[\xc2]' not in msg:
            res2 = False
        print(msg)

        node_ex1.set_current_conf('MAIN', reverse=True, root_regexp=None)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value()
        if b' ~(..)~ ' in msg or b' ~(X)~ ' in msg or b'[<]' in msg or b'[\xc2]' in msg:
            res2 = False
        print(msg)

        node_ex1 = dm.get_data('EX1')

        node_ex1.set_current_conf('ALT', root_regexp='TC/KV')
        node_ex1.set_current_conf('ALT', root_regexp='TUX$')

        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value()
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg or b'[<]' not in msg or b'[\xc2]' not in msg:
            res2 = False
        print(msg)

        print('\n***** test 8.2.1: subparts equality:')

        val1 = node_ex1.get_node_by_path('TUX$').get_flatten_value()
        val2 = node_ex1.get_node_by_path('CONCAT$').get_flatten_value()
        print(b' @ ' + val1 + b' @ ')
        print(val2)

        res21 = b' @ ' + val1 + b' @ ' == val2

        print(res2, res21)

        print('\n*** test 8.3:')

        node_ex1 = dm.get_data('EX1')

        res3 = True
        l = sorted(node_ex1.get_nodes_names(conf='ALT'))
        for k in l:
            print(k)
            if 'EX1' != k[0][:len('EX1')]:
                res3 = False
                break

        print('\n*** test 8.4:')

        print(node_ex1.get_flatten_value())
        res4 = True
        l = sorted(node_ex1.get_nodes_names())
        for k in l:
            print(k)
            if 'EX1' != k[0][:len('EX1')]:
                res4 = False
                break

        print('\n*** test 8.5:')

        node_ex1 = dm.get_data('EX1')

        res5 = True
        node_ex1.unfreeze_all()
        msg = node_ex1.get_node_by_path('TUX$').get_flatten_value(conf='ALT', recursive=False)
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' in msg:
            res5 = False
        print(msg)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_node_by_path('TUX$').get_flatten_value(conf='ALT', recursive=True)
        if b' ~(..)~ ' not in msg or b' ~(X)~ ' not in msg:
            res5 = False
        print(msg)


        print('\n*** test 8.6:')

        node_ex1 = dm.get_data('EX1')

        # attr3 = Elt_Attributes(defaults=False)
        # attr3.conform_to_nonterm_node()
        # attr3.enable_conf('ALT')

        # node_kind3 = [NodeInternals_NonTerm]

        crit = NodeInternalsCriteria(mandatory_attrs=[NodeInternals.Mutable],
                                    node_kinds=[NodeInternals_NonTerm])

        node_ex1.unfreeze_all()

        l = tux2.get_reachable_nodes(internals_criteria=crit, owned_conf='ALT')

        for e in l:
            print(e.get_path_from(tux2))

        if len(l) == 2:
            res6 = True
        else:
            res6 = False


        print('Results:')
        print(res0, res1, res2, res21, res3, res4, res5, res6)

        results['test8'] = res0 and res1 and res2 and res21 and res3 and res4 and res5 and res6


        print('\n### TEST 9: test the constraint type: =+(w1,w2,...)\n' \
                  '--> can be False in really rare case')

        node_ex1 = dm.get_data('EX1')

        res = True
        for i in range(20):
            node_ex1.unfreeze_all()
            msg = node_ex1.get_node_by_path('TUX$').get_flatten_value(conf='ALT', recursive=True)
            if b' ~(..)~ TUX ~(..)~ ' not in msg:
                res = False
                break
            # print(msg)

        results['test9'] = res


        print('\n### TEST 10: test fuzzing primitives')

        print('\n*** test 10.1: fuzz_data_tree()')

        node_ex1 = dm.get_data('EX1')
        fuzz_data_tree(node_ex1)
        node_ex1.get_value()



        print('\n### TEST 11: test terminal Node alternate conf')

        print('\n*** test 11.1: value type Node')

        node_ex1 = dm.get_data('EX1')

        res1 = True
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b'[<]' not in msg or b'[\xc2]' not in msg:
            res1 = False
        print(msg)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b'[<]' not in msg or b'[\xc2]' not in msg:
            res1 = False
        print(msg)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_node_by_path('TUX$').get_flatten_value(conf='ALT', recursive=False)
        if b'[<]' in msg or b'[\xc2]' in msg or b' ~(..)~ TUX ~(..)~ ' not in msg:
            res1 = False
        print(msg)


        print('\n*****\n')

        crit = NodeInternalsCriteria(mandatory_attrs=[NodeInternals.Mutable],
                                    node_kinds=[NodeInternals_TypedValue])

        node_ex1.unfreeze_all()

        l = node_ex1.get_reachable_nodes(internals_criteria=crit, owned_conf='ALT')

        for e in l:
            print(e.get_path_from(node_ex1))

        if len(l) == 4:
            res2 = True
        else:
            res2 = False


        print('\n*** test 11.2: func type Node')

        node_ex1 = dm.get_data('EX1')

        res3 = True
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b'___' not in msg:
            res3 = False
        print(msg)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_flatten_value(conf='ALT')
        if b'___' not in msg:
            res3 = False
        print(msg)

        node_ex1.unfreeze_all()
        msg = node_ex1.get_node_by_path('TUX$').get_flatten_value(conf='ALT', recursive=False)
        if b'___' in msg:
            res3 = False
        print(msg)


        print(res1, res2, res3)
        results['test11'] = res1 and res2 and res3

        # raise ValueError


        print('\n### TEST 12: get_all_path() test')

        print('\n*** test 12.1:')

        node_ex1 = dm.get_data('EX1')
        htbl = node_ex1.get_all_paths()
        l = sorted(list(htbl.keys()))
        for i in l:
            print(i)

        print('\n******\n')

        node_ex1.get_value()
        htbl = node_ex1.get_all_paths()
        l = sorted(list(htbl.keys()))
        for i in l:
            print(i)

        print('\n******\n')

        node_ex1.unfreeze_all()
        node_ex1.get_value()
        htbl = node_ex1.get_all_paths()
        l = sorted(list(htbl.keys()))
        for i in l:
            print(i)

        print('\n*** test 13: test typed_value Node')

        print('\n*** test 13.1:')

        tux = dm.get_data('TUX')

        crit = NodeInternalsCriteria(mandatory_attrs=[NodeInternals.Mutable],
                                     node_kinds=[NodeInternals_TypedValue])

        print('> before changing types:')

        vt = {}
        l1 = tux.get_reachable_nodes(internals_criteria=crit)
        for e in l1:
            print('Node.name: ', e.name, ', Id: ', e)
            print('Node.env: ', e.env)
            print('Node.value_type: ', e.cc.get_value_type())
            vt[e] = e.cc.get_value_type()
            if issubclass(vt[e].__class__, VT_Alt): #isinstance(vt[e], BitField) or isinstance(vt[e], String):
                continue
            compat = list(vt[e].compat_cls.values())
            compat.remove(vt[e].__class__)
            print('Compatible types: ', compat)

            c = random.choice(compat)
            # while True:
            #     c = random.choice(compat)
            #     if c != vt[e].__class__:
            #         break

            e.set_values(value_type=c())

        res1 = False
        if len(l1) == 13:
            res1 = True

        print('\n> after changing types:')

        l1 = tux.get_reachable_nodes(internals_criteria=crit)
        for e in l1:
            print('Node.name', e.name)
            print('Node.value_type:', e.cc.get_value_type())
            new_vt = e.cc.get_value_type()
            # if isinstance(new_vt, BitField):
            if issubclass(vt[e].__class__, VT_Alt):
                continue
            if new_vt.__class__ == vt[e].__class__:
                res2 = False
                break
            else:
                res2 = True

        # print(res1, res2)
        # raise ValueError

        print('\n*** test 13.2:')

        evt = dm.get_data('TVE')
        l = evt.get_reachable_nodes(internals_criteria=crit)

        print('\n> part1:\n')

        print('--[ EVT1 ]-----[ EVT2 ]--')
        for i in range(7):
            print(evt.get_flatten_value())
            evt.unfreeze_all()

        vt = {}
        for e in l:
            print('-----')
            print('Node.name:          ', e.name)
            print('Node.env:           ', e.env)
            print('Node.value_type:    ', e.cc.get_value_type())
            vt[e] = e.cc.get_value_type()
            # if isinstance(vt[e], BitField):
            if issubclass(vt[e].__class__, VT_Alt):
                continue
            compat = list(vt[e].compat_cls.values())
            print('Compatible types:  ', compat)
            fuzzy = list(vt[e].fuzzy_cls.values())
            print('Fuzz compat types: ', fuzzy)
            c = random.choice(fuzzy)
            e.set_values(value_type=c())
            print("Set new value type '%s' for the Node %s!" % (c, e.name))


        print('\n> part2:\n')

        print('--[ EVT1 ]-----[ EVT2 ]--')
        for i in range(20):
            s = evt.get_flatten_value()
            print(s)
            if evt.env.exhausted_node_exists():
                print("Exhausted Elts Exists!")
                l = evt.env.get_exhausted_nodes()
                for e in l:
                    evt.env.clear_exhausted_node(e)
                    print('Node %s has been cleared!' % e.name)
                    if e.is_value():
                        continue
                    vt = e.cc.get_value_type()
                    if isinstance(vt, BitField):
                        continue
                    if vt:
                        compat = list(vt.compat_cls.values())
                        compat.remove(vt.__class__)
                        c = random.choice(compat)
                        e.set_values(value_type=c())
                        print("Set new value type '%s' for the Node %s!" % (c, e.name))


            evt.unfreeze_all()


        print(res1, res2)
        results['test13'] = res1 and res2


        print('\n*** test 14: test Proxy Node')

        res1 = False

        blend = dm.get_data('BLEND')
        msg = blend.get_flatten_value()
        print('Blend Node starts with:')
        print(msg[:300] + b' ...')
        print('\nAnd ends with:')
        print(b'... ' + msg[len(msg)-300:len(msg)])

        print("\n--> Call unfreeze()")
        blend.unfreeze()

        msg2 = blend.get_flatten_value()

        print('\nBlend Node starts with:')
        print(msg2[:300] + b' ...')
        print('\nAnd ends with:')
        print(b'... ' + msg2[len(msg2)-300:len(msg2)])

        print('\n### SUMMARY ###')

        for k, v in results.items():
            print('is %s OK? %r' % (k, v))

        for v in results.values():
            self.assertTrue(v)



class TestMisc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dm = example.data_model
        cls.dm.load_data_model(fuzzer._name2dm)


    def setUp(self):
        pass


    def _loop_nodes(self, node, cpt=20, criteria_func=None, transform=lambda x: x):
        stop_loop = False
        for i in range(cpt):
            if stop_loop:
                break
            node.unfreeze()
            
            print("[#%d] " % i, transform(node.get_flatten_value()))
            if node.env.exhausted_node_exists():
                for e in node.env.get_exhausted_nodes():
                    if criteria_func(e):
                        print('--> exhausted node: ', e.name)
                        stop_loop = True
                        break
                node.env.clear_all_exhausted_nodes()

        return i

    # @unittest.skip("demonstrating skipping")    
    def test_Node_unfreeze_dont_change_state(self):
        '''
        unfreeze(dont_change_state)
        '''
        simple = self.dm.get_data('Simple')

        simple.make_determinist(recursive=True)
        for i in range(15):
            simple.unfreeze()
            val1 = simple.get_flatten_value()
            # print(val1)
            simple.unfreeze(dont_change_state=True)
            val2 = simple.get_flatten_value()
            # print(val2)
            if val1 != val2:
                res1 = False
                break
        else:
            res1 = True

        self.assertTrue(res1)


    def test_TypedNode_1(self):
        evt = dm.get_data('TVE')
        evt.get_value()

        print('=======[ PATHS ]========')

        htbl = evt.get_all_paths()
        l = sorted(list(htbl.keys()))
        for i in l:
            print(i)

        print('\n=======[ Typed Nodes ]========')

        c = NodeInternalsCriteria(node_kinds=[NodeInternals_TypedValue])

        vt = {}
        l = evt.get_reachable_nodes(internals_criteria=c)
        for e in l:
            print('------------')
            print('  Node.name:           ', e.name)
            print('  Node.env:            ', e.env)
            print('  Node.value_type:     ', e.cc.get_value_type())
            vt[e] = e.cc.get_value_type()
            if issubclass(vt[e].__class__, VT_Alt):
                continue
            compat = list(vt[e].compat_cls.values())
            print('  Compatible types:   ', compat)
            fuzzy = list(vt[e].fuzzy_cls.values())
            print('  Fuzz compat types:  ', fuzzy)

        print('')

        evt = dm.get_data('TVE')
        evt.make_finite(all_conf=True, recursive=True)
        evt.make_determinist(all_conf=True, recursive=True)
        evt.show()
        # evt.get_value()
        mem = Memory()
        prev_path = None
        turn_nb_list = []
        for i in range(150):
            print('=======[ %d ]========' % i)
            print('  orig:    ', evt.get_flatten_value())
            print('  ----')
            node, orig_node_val, remaining = fuzz_typed_values(mem, evt)
            if node != None:
                print('  fuzzed:  ', evt.get_flatten_value())
                print('  ----')
                current_path = node.get_path_from(evt)
                if current_path != prev_path:
                    turn_nb_list.append(i)
                print('  current fuzzed node:     %s' % current_path)
                prev_path = current_path
                vt = node.cc.get_value_type()
                print('  node value type:        ', vt)
                if issubclass(vt.__class__, VT_Alt): #issubclass(vt.__class__, BitField):
                    print('  |- node fuzzy mode:        ', vt._fuzzy_mode)
                print('  node value type determinist:        ', vt.determinist)
                print('  node determinist:        ', node.cc.is_attr_set(NodeInternals.Determinist))
                print('  node finite:        ', node.cc.is_attr_set(NodeInternals.Finite))
                if not issubclass(vt.__class__, VT_Alt):
                    print('  node vt endian:         ', node.cc.get_value_type().endian)
                print('  node orig value:        (hexlified) {0!s:s}, {0!s:s}'.format(binascii.hexlify(orig_node_val),
                                                                                     orig_node_val))
                print('  node corrupted value:   (hexlified) {0!s:s}, {0!s:s}'.format(binascii.hexlify(node.get_flatten_value()),
                                                                                     node.get_flatten_value()))
                print('  remaining nodes:         %d' % remaining)
            else:
                turn_nb_list.append(i)
                print('\n--> Fuzzing terminated!\n')
                break

        print('\nTurn number when Node has changed: %r, number of test cases: %d' % (turn_nb_list, i))
        good_list = [0, 9, 19, 25, 34, 40, 53, 65, 73, 81, 89, 97, 105]
        
        msg = "If Fuzzy_<TypedValue>.int_list have been modified in size, the good_list should be updated.\n" \
              "If BitField are in random mode [currently put in determinist mode], the fuzzy_mode can produce more" \
              " or less value depending on drawn value when .get_value() is called (if the drawn value is" \
              " the max for instance, drawn_value+1 will not be produced)"

        self.assertTrue(i == good_list[-1] and turn_nb_list == good_list, msg=msg)


    def test_Node_Attr_01(self):
        '''
        Value Node make_random()/make_determinist()
        TODO: NEED assertion
        '''
        evt = dm.get_data('TVE')

        for i in range(10):
            evt.unfreeze()
            print(evt.get_flatten_value())

        evt.get_node_by_path('Pre').make_random()

        print('******')

        for i in range(10):
            evt.unfreeze()
            print(evt.get_flatten_value())

        # self.assertEqual(idx, )

    def test_NonTerm_Attr_01(self):
        '''
        make_determinist()/finite() on NonTerm Node
        TODO: NEED assertion
        '''
        loop_count = 20

        crit_func = lambda x: x.name == 'NonTerm'

        print('\n -=[ random & infinite (loop count: %d) ]=- \n' % loop_count)

        nt  = dm.get_data('NonTerm')
        # nt.make_infinite(all_conf=True, recursive=True)
        self._loop_nodes(nt, loop_count, criteria_func=crit_func)

        print('\n -=[ random & finite (loop count: %d) ]=- \n' % loop_count)

        nt = dm.get_data('NonTerm')
        nt.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(nt, loop_count, criteria_func=crit_func)

        print('\n -=[ determinist & finite (loop count: %d) ]=- \n' % loop_count)

        nt  = dm.get_data('NonTerm')
        nt.make_finite(all_conf=True, recursive=True)
        nt.make_determinist(all_conf=True, recursive=True)
        self._loop_nodes(nt, loop_count, criteria_func=crit_func)

        print('\n -=[ determinist & infinite (loop count: %d) ]=- \n' % loop_count)

        nt  = dm.get_data('NonTerm')
        nt.make_infinite(all_conf=True, recursive=True)
        nt.make_determinist(all_conf=True, recursive=True)
        self._loop_nodes(nt, loop_count, criteria_func=crit_func)

        

    def test_BitField_Attr_01(self):
        '''
        make_determinist()/finite() on BitField Node
        TODO: NEED assertion
        '''

        loop_count = 80

        print('\n -=[ random & infinite (loop count: %d) ]=- \n' % loop_count)

        t = BitField(subfield_limits=[2,6,10,12],
                     subfield_val_lists=[[4,2,1], [2,15,16,3], None, [1]],
                     subfield_val_extremums=[None, None, [3,11], None],
                     padding=0, lsb_padding=True, endian=VT.LittleEndian)
        node = Node('BF', value_type=t)
        node.set_env(Env())
        node.make_random(all_conf=True, recursive=True)
        self._loop_nodes(node, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n -=[ determinist & infinite (loop count: %d) ]=- \n' % loop_count)


        node_copy = Node('BF_copy', base_node=node, ignore_frozen_state=True)
        node_copy.set_env(Env())
        node_copy.make_determinist(all_conf=True, recursive=True)
        self._loop_nodes(node_copy, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n -=[ determinist & finite (loop count: %d) ]=- \n' % loop_count)

        node_copy2 = Node('BF_copy2', base_node=node, ignore_frozen_state=True)
        node_copy2.set_env(Env())
        node_copy2.make_determinist(all_conf=True, recursive=True)
        node_copy2.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(node_copy2, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n -=[ random & finite (loop count: %d) ]=- \n' % loop_count)

        node_copy3 = Node('BF_copy3', base_node=node, ignore_frozen_state=True)
        node_copy3.set_env(Env())
        node_copy3.make_random(all_conf=True, recursive=True)
        node_copy3.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(node_copy3, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)


    def test_BitField(self):

        loop_count = 20
        e_bf = Node('BF')
        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[4,2,1], None, [10,13]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=0, lsb_padding=False, endian=VT.BigEndian)
        e_bf.set_values(value_type=vt)
        e_bf.set_env(Env())
        e_bf.make_determinist(all_conf=True, recursive=True)
        e_bf.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(e_bf, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n***\n')

        e_bf.cc.value_type.switch_mode()
        self._loop_nodes(e_bf, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n***\n')

        e_bf.cc.value_type.switch_mode()
        self._loop_nodes(e_bf, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n***')
        print('We change the current BitField value:')
        e_bf.unfreeze_all()
        print(binascii.b2a_hex(e_bf.get_value()))
        e_bf.unfreeze_all()
        print(binascii.b2a_hex(e_bf.get_value()), '\n')

        e_bf.cc.value_type.switch_mode()
        self._loop_nodes(e_bf, loop_count, criteria_func=lambda x: True, transform=binascii.b2a_hex)

        print('\n***')
        print('Random & finite: (should result in only 1 possible values)')

        vt = BitField(subfield_sizes=[4,4], subfield_val_lists=[[0x3], [0xF]])
        e = Node('bf_test', value_type=vt)
        e.set_env(Env())
        e.make_finite()
        e.make_random()
        count = self._loop_nodes(e, loop_count, criteria_func=lambda x: True)

        self.assertEqual(count, 1)

        
    def test_BitField_basic_features(self):

        print('\n***** [ BitField ] *****\n')

        i = 0
        ok = True
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=0, lsb_padding=False, endian=VT.LittleEndian)
        val = binascii.b2a_hex(t.get_value())
        print(t.pretty_print(), t.drawn_val)
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val, b'4501')
            
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=0, lsb_padding=True, endian=VT.BigEndian)
        val = binascii.b2a_hex(t.get_value())
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val, b'5140')
                 
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=1, lsb_padding=True, endian=VT.BigEndian)
        val = binascii.b2a_hex(t.get_value())
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val, b'517f')
                         
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=0, lsb_padding=False, endian=VT.BigEndian)
        val = binascii.b2a_hex(t.get_value())
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val,b'0145')
                 
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=1, lsb_padding=False, endian=VT.BigEndian)
        val = binascii.b2a_hex(t.get_value())
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val, b'fd45')
                 
        t = BitField(subfield_sizes=[2,4,2,2], subfield_val_lists=[[1],[1],[1],[1]],
                     padding=1, lsb_padding=False, endian=VT.BigEndian)
        val = binascii.b2a_hex(t.get_value())
        print('*** [%d] ' % i, val)
        i += 1
        self.assertEqual(val,b'fd45')
                 

        print('\n******** subfield_val_list\n')

        # Note that 4 in subfield 1 and 16 in subfield 2 are ignored
        # --> 6 different values are output before looping
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_lists=[[4,2,1],[2,15,16,3],[2,3,0],[1]],
                     padding=0, lsb_padding=True, endian=VT.LittleEndian, determinist=True)
        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)

        print('\n********\n')

        val = collections.OrderedDict()
        t.switch_mode()
        for i in range(30):
            val[i] = binascii.b2a_hex(t.get_value())
            print(t.pretty_print(), ' --> ', t.get_current_raw_val())
            print('*** [%d] ' % i, val[i])


        print(list(val.values())[:13])
        self.assertEqual(list(val.values())[:13],
                         [b'c062',b'0062',b'4062',b'806f', b'8060',b'8063',b'8061',b'8072',
                          b'8042',b'8052',b'80e2',b'8022',b'80a2'])
        
        print('\n********\n')

        t.switch_mode()
        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)


        print('\n******** subfield_val_extremums\n')

        # --> 14 different values are output before looping
        t = BitField(subfield_limits=[2,6,8,10], subfield_val_extremums=[[1,2],[4,12],[0,3],[2,3]],
                     padding=0, lsb_padding=True, endian=VT.LittleEndian, determinist=True)
        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)

        print('\n********\n')

        t.switch_mode()
        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)


        print('\n********\n')

        t.switch_mode()
        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)


        print('\n******** rewind() tests \n')

        t = BitField(subfield_limits=[2,6,8,10],
                     subfield_val_extremums=[[1,2],[4,12],[0,3],None],
                     subfield_val_lists=[None, None, None, [3]],
                     padding=0, lsb_padding=False, endian=VT.BigEndian, determinist=True)

        val = {}
        for i in range(30):
            val[i] = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val[i])
            if t.is_exhausted():
                break


        if val[0] != b'0311' or val[1] != b'0312' or val[2] != b'0316' or val[3] != b'031a' \
           or val[4] != b'031e' or val[5] != b'0322' or val[6] != b'0326' or val[7] != b'032a' \
                        or val[8] != b'032e' or val[9] != b'0332' or val[10] != b'0372' or val[11] != b'03b2' or val[12] != b'03f2':
            raise ValueError


        print('\n********\n')
        t.reset_state()

        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))
        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))

        print('\n********\n')

        t.reset_state()

        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)
            if t.is_exhausted():
                break

        print('\n********\n')

        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))


        print('\n******** Fuzzy mode\n')
        t.reset_state()
        t.switch_mode()

        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))
        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))

        print('\n********\n')

        t.reset_state()
        t.switch_mode()

        for i in range(30):
            val = binascii.b2a_hex(t.get_value())
            print('*** [%d] ' % i, val)
            if t.is_exhausted():
                break

        print('\n********\n')

        print('--> rewind')
        t.rewind()
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))
        print(binascii.b2a_hex(t.get_value()))




        
    def test_BitField_various_features(self):

        bf = Node('BF')
        vt1 = BitField(subfield_sizes=[3,5,7],
                      subfield_val_lists=[[2,1], None, [10,120]],
                      subfield_val_extremums=[None, [6, 15], None],
                      padding=0, lsb_padding=True, endian=VT.BigEndian)
        bf.set_values(value_type=vt1)
        bf.make_determinist(all_conf=True, recursive=True)
        bf.set_env(Env())

        print('\n -=[ .extend_right() method ]=- \n')
        print('*** before extension')
        
        bf.show()
        # print(bf.get_raw_value())
        # bf.unfreeze()
        # bf.show()
        
        vt2 = BitField(subfield_sizes=[4,3,4,4,2],
                       subfield_val_lists=[None, [3,5], [15], [14], [2]],
                       subfield_val_extremums=[[8, 12], None, None, None, None],
                       padding=0, lsb_padding=False, endian=VT.BigEndian)


        print('*** after extension')

        bf.unfreeze()
        bf.value_type.extend_right(vt2)
        bf.show()

        vt = bf.value_type
        self.assertEqual(vt.subfield_limits, [3, 8, 15, 19, 22, 26, 30, 32])
        # self.assertEqual(vt.subfield_limits, [3, 8, 16, 20, 23, 27, 31, 33])
        print('\n -=[ .set_subfield() .get_subfield() methods ]=- \n')

        vt.set_subfield(idx=3, val=5)
        vt.set_subfield(idx=0, val=3)
        self.assertEqual(vt.get_subfield(idx=3), 5)
        self.assertEqual(vt.get_subfield(idx=0), 3)

        bf.unfreeze()
        bf.show()
        
        self.assertEqual(bf.value_type.get_subfield(idx=3), 5)
        self.assertEqual(bf.value_type.get_subfield(idx=0), 3)
        
        
    def test_BitField_absorb(self):

        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[3,2,0xe,1], None, [10,13,3]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=1,  endian=VT.BigEndian, lsb_padding=True)
        bfield_1 = Node('bfield_1', value_type=vt)
        # bfield.set_env(Env())

        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[3,2,0xe,1], None, [10,13,3]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=0,  endian=VT.BigEndian, lsb_padding=True)
        bfield_2 = Node('bfield_2', value_type=vt)

        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[3,2,0xe,1], None, [10,13,3]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=1,  endian=VT.BigEndian, lsb_padding=False)
        bfield_3 = Node('bfield_3', value_type=vt)

        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[3,2,0xe,1], None, [10,13,3]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=0,  endian=VT.BigEndian, lsb_padding=False)
        bfield_4 = Node('bfield_4', value_type=vt)

        # '?\xef' (\x3f\xe0) + padding 0b1111
        msg = struct.pack('>H', 0x3fe0 + 0b1111)
        status, off, size, name = bfield_1.absorb(msg, constraints=AbsFullCsts())

        print('\n ---[message to absorb]---')
        print(repr(msg))
        bfield_1.show()
        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))


        msg = struct.pack('>H', 0x3fe0)
        status, off, size, name = bfield_2.absorb(msg, constraints=AbsFullCsts())

        print('\n ---[message to absorb]---')
        print(repr(msg))
        bfield_2.show()
        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))

        msg = struct.pack('>H', 0xf3fe)
        status, off, size, name = bfield_3.absorb(msg, constraints=AbsFullCsts())

        print('\n ---[message to absorb]---')
        print(repr(msg))
        bfield_3.show()
        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))

        msg = struct.pack('>H', 0x3fe)
        status, off, size, name = bfield_4.absorb(msg, constraints=AbsFullCsts())
        
        print('\n ---[message to absorb]---')
        print(repr(msg))
        bfield_4.show()
        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))


    def test_MISC(self):
        '''
        TODO: assertion + purpose
        '''
        loop_count = 20

        e = Node('VT1')
        vt = UINT16_be(int_list=[1,2,3,4,5,6])
        e.set_values(value_type=vt)
        e.set_env(Env())
        e.make_determinist(all_conf=True, recursive=True)
        e.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(e, loop_count, criteria_func=lambda x: True)

        e2 = Node('VT2', base_node=e, ignore_frozen_state=True)
        e2.set_env(Env())
        e2.make_determinist(all_conf=True, recursive=True)
        e2.make_finite(all_conf=True, recursive=True)
        self._loop_nodes(e2, loop_count, criteria_func=lambda x: True)

        print('\n****\n')

        sep = Node('sep', values=[' # '])
        nt = Node('NT')
        nt.set_subnodes_with_csts([
                1, ['u>', [e, 3], [sep, 1], [e2, 2]]
                ])
        nt.set_env(Env())

        self._loop_nodes(nt, loop_count, criteria_func=lambda x: True)

        print('\n****\n')

        v = dm.get_data('V1_middle')
        v.make_finite()

        e = Node('NT')
        e.set_subnodes_with_csts([
                1, ['u>', [v, 2]]
                ])
        e.set_env(Env())
        e.make_determinist(recursive=True)
        self._loop_nodes(e, loop_count, criteria_func=lambda x: True)

        print('\n****\n')

        self._loop_nodes(e, loop_count, criteria_func=lambda x: True)

        print('\n****\n')

        e = dm.get_data('Middle_NT')
        e.make_finite(all_conf=True, recursive=True)
        e.make_determinist(all_conf=True, recursive=True)
        self._loop_nodes(e, loop_count, criteria_func=lambda x: x.name == 'Middle_NT')



class TestModelWalker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dm = example.data_model
        cls.dm.load_data_model(fuzzer._name2dm)

    def setUp(self):
        pass

    def test_NodeConsumerStub_1(self):
        nt  = self.dm.get_data('Simple')
        default_consumer = NodeConsumerStub()
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(nt, default_consumer, make_determinist=True, max_steps=70):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 37)
        
    def test_NodeConsumerStub_2(self):
        nt  = self.dm.get_data('Simple')
        default_consumer = NodeConsumerStub(max_runs_per_node=-1, min_runs_per_node=2)
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(nt, default_consumer, make_determinist=True, max_steps=70):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 26)


    def test_BasicVisitor(self):
        nt  = self.dm.get_data('Simple')
        default_consumer = BasicVisitor()
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(nt, default_consumer, make_determinist=True, max_steps=70):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 29)

    def test_NonTermVisitor(self):
        simple  = self.dm.get_data('Simple')
        nonterm_consumer = NonTermVisitor()
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, nonterm_consumer, make_determinist=True, max_steps=10):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 4)

    def test_TypedNodeDisruption_1(self):
        nt  = self.dm.get_data('Simple')
        tn_consumer = TypedNodeDisruption()
        ic = NodeInternalsCriteria(negative_node_subkinds=[String])
        tn_consumer.set_node_interest(internals_criteria=ic)
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(nt, tn_consumer, make_determinist=True, max_steps=100):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 23) # 23 when no String()


    def test_TypedNodeDisruption_2(self):
        nt  = self.dm.get_data('Simple')
        tn_consumer = TypedNodeDisruption(max_runs_per_node=3, min_runs_per_node=3)
        ic = NodeInternalsCriteria(negative_node_subkinds=[String])
        tn_consumer.set_node_interest(internals_criteria=ic)
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(nt, tn_consumer, make_determinist=True, max_steps=100):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 9)


    def test_TermNodeDisruption_1(self):
        simple  = self.dm.get_data('Simple')
        consumer = TermNodeDisruption()
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=-1):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
            # print('original val: %s' % repr(orig_node_val))
            # print('corrupted val: %s' % repr(consumed_node.get_flatten_value()))
        self.assertEqual(idx, 245)

    def test_TermNodeDisruption_2(self):
        simple  = self.dm.get_data('Simple')
        consumer = TermNodeDisruption(max_runs_per_node=-1, min_runs_per_node=2)
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=78):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 78)

    def test_TermNodeDisruption_3(self):
        simple  = self.dm.get_data('Simple')
        consumer = TermNodeDisruption(specific_args=['1_BANG_1', '2_PLOUF_2'])
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=-1):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 140)


    def test_AltConfConsumer_1(self):
        simple  = self.dm.get_data('Simple')
        consumer = AltConfConsumer(max_runs_per_node=-1, min_runs_per_node=-1)
        consumer.set_node_interest(owned_confs=['ALT'])

        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=50):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 11)

    def test_AltConfConsumer_2(self):
        simple  = self.dm.get_data('Simple')
        consumer = AltConfConsumer(max_runs_per_node=2, min_runs_per_node=1)
        consumer.set_node_interest(owned_confs=['ALT'])

        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=50):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 6)

    def test_AltConfConsumer_3(self):
        simple  = self.dm.get_data('Simple')
        consumer = AltConfConsumer(max_runs_per_node=-1, min_runs_per_node=-1)
        consumer.set_node_interest(owned_confs=['ALT', 'ALT_2'])

        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=50):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 17)

    def test_AltConfConsumer_4(self):
        simple  = self.dm.get_data('Simple')
        consumer = AltConfConsumer(max_runs_per_node=-1, min_runs_per_node=-1)
        consumer.set_node_interest(owned_confs=['ALT_2', 'ALT'])

        for rnode, consumed_node, orig_node_val, idx in ModelWalker(simple, consumer, make_determinist=True, max_steps=50):
            print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))
        self.assertEqual(idx, 17)


    def test_JPG(self):
        '''
        Test assertion depends on input JPG
        TODO: include specific jpg, to fix assertion
        '''
        nt = self.dm.get_data('JPG')
        tn_consumer = TypedNodeDisruption()

        walker = iter(ModelWalker(nt, tn_consumer, make_determinist=True))
        while True:
            try:
                rnode, consumed_node, orig_node_val, idx = next(walker)
                # rnode.get_value()
            except StopIteration:
                break

        print(colorize('number of imgs: %d'%idx, rgb=Color.INFO))

        # self.assertEqual(idx, )


    def test_USB(self):
        dm_usb = fmk.get_data_model_by_name('usb')
        dm_usb.build_data_model()

        data  = dm_usb.get_data('CONF')
        consumer = TypedNodeDisruption()
        consumer.need_reset_when_structure_change = True
        for rnode, consumed_node, orig_node_val, idx in ModelWalker(data, consumer, make_determinist=True, max_steps=600):
            pass
            # print(colorize('[%d] '%idx + repr(rnode.get_flatten_value()), rgb=Color.INFO))

        print(colorize('number of confs: %d'%idx, rgb=Color.INFO))

        self.assertEqual(idx, 150) # previously 189



class TestNodeFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_absorb_nonterm_1(self):
        nint_1 = Node('nint1', value_type=UINT16_le(int_list=[0xabcd]))
        nint_2 = Node('nint2', value_type=UINT8(int_list=[0xf]))
        nint_3 = Node('nint3', value_type=UINT16_be(int_list=[0xeffe]))

        nstr_1 = Node('str1', value_type=String(val_list=['TBD1'], max_sz=5))
        nstr_2 = Node('str2', value_type=String(val_list=['TBD2'], max_sz=8))

        vt = BitField(subfield_sizes=[4,4,4],
                      subfield_val_lists=[[3,2,0xe,1], None, [10,13,3]],
                      subfield_val_extremums=[None, [14, 15], None],
                      padding=1,  endian=VT.BigEndian, lsb_padding=True)

        bfield = Node('bfield', value_type=vt)
        bfield.enforce_absorb_constraints(AbsCsts())

        top = Node('top')
        top.set_subnodes_with_csts([
            1, ['u>', [nint_1, 1], [nint_2, 2], [nstr_1, 1], [nint_3, 2], [nstr_2, 1], [bfield, 1]]
        ])

        top.set_env(Env())

        # '?\xef' (\x3f\xe0) + padding 0b1111
        msg_tail = struct.pack('>H', 0x3fe0 + 0b1111)
        
        msg = b'\xe1\xe2\xff\xeeCOOL!\xc1\xc2\x88\x9912345678' + msg_tail
        status, off, size, name = top.absorb(msg, constraints=AbsNoCsts(size=True))
        
        print('\n ---[message to absorb]---')
        print(repr(msg))
        print('\n ---[absobed message]---')
        print(top.get_value())

        top.show()

        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))

    def test_absorb_nonterm_2(self):
        nint_1 = Node('nint1', value_type=UINT16_le(int_list=[0xcdab, 0xffee]))
        nint_2 = Node('nint2', value_type=UINT8(int_list=[0xaf, 0xbf, 0xcf]))
        nint_3 = Node('nint3', value_type=UINT16_be(int_list=[0xcfab, 0xeffe]))

        nstr_1 = Node('str1', value_type=String(val_list=['STR1', 'str1'], max_sz=5))
        nstr_2 = Node('str2', value_type=String(val_list=['STR22', 'str222'], max_sz=8))

        top = Node('top')
        top.set_subnodes_with_csts([
            1, ['u=.', [nint_1, 1], [nint_2, 1, 2], [nstr_1, 1], [nint_3, 2], [nstr_2, 1]]
        ])

        top.set_env(Env())

        # 2*nint_3 + nstr_1 + nstr_2 + 2*nint_2 + nint_1
        msg = '\xef\xfe\xef\xfeSTR1str222\xcf\xab\xcd'
        status, off, size, name = top.absorb(msg)
        
        print('\n ---[message to absorb]---')
        print(repr(msg))
        print('\n ---[absobed message]---')
        print(top.get_value())

        top.show(alpha_order=True)

        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))


    def test_absorb_nonterm_3(self):
        nint_1 = Node('nint1', value_type=UINT16_le(int_list=[0xcdab, 0xffee]))
        nint_2 = Node('nint2', value_type=UINT8(int_list=[0xaf, 0xbf, 0xcf]))
        nint_3 = Node('nint3', value_type=UINT16_be(int_list=[0xcfab, 0xeffe]))

        nstr_1 = Node('str1', value_type=String(val_list=['STR1', 'str1'], max_sz=5))
        nstr_2 = Node('str2', value_type=String(val_list=['STR22', 'str222'], max_sz=8))

        top = Node('top')
        top.set_subnodes_with_csts([
            1, ['u=+(2,2,1,5,1)', [nint_1, 1], [nint_2, 1], [nstr_1, 1], [nint_3, 2], [nstr_2, 1, 3]]
        ])

        top.set_env(Env())

        msg = 'str222str222'
        status, off, size, name = top.absorb(msg)
        
        print('\n ---[message to absorb]---')
        print(repr(msg))
        print('\n ---[absobed message]---')
        print(top.get_value())

        top.show(alpha_order=True)

        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(size, len(msg))


    def test_intg_absorb_1(self):

        self.helper1_called = False
        self.helper2_called = False

        def nint_1_helper(blob, constraints, node_internals):
            if blob[:1] in [b'\xe1', b'\xcd']:
                return AbsorbStatus.Accept, 0, None
            else:
                return AbsorbStatus.Reject, 0, None

        def nint_1_alt_helper(blob, constraints, node_internals):
            if blob[:1] == b'\xff':
                return AbsorbStatus.Accept, 0, None
            else:
                self.helper1_called = True
                return AbsorbStatus.Reject, 0, None

        nint_1 = Node('nint1', value_type=UINT16_le(int_list=[0xabcd, 0xe2e1]))
        nint_1.set_absorb_helper(nint_1_helper)

        nint_1_alt = Node('nint1_alt', value_type=UINT16_le(int_list=[0xabff, 0xe2ff]))
        nint_1_alt.set_absorb_helper(nint_1_alt_helper)

        nint_2 = Node('nint2', value_type=UINT8(int_list=[0xf, 0xff, 0xee]))
        nint_3 = Node('nint3', value_type=UINT16_be(int_list=[0xeffe, 0xc1c2, 0x8899]))

        nstr_1 = Node('cool', value_type=String(val_list=['TBD1'], size=4, ascii_mode=True))
        nstr_1.enforce_absorb_constraints(AbsNoCsts(regexp=True))
        nstr_2 = Node('str2', value_type=String(val_list=['TBD2TBD2', '12345678'], size=8, ascii_mode=True))

        nint_50 = Node('nint50', value_type=UINT8(int_list=[0xaf, 0xbf, 0xcf]))
        nint_51 = Node('nint51', value_type=UINT16_be(int_list=[0xcfab, 0xeffe]))
        nstr_50 = Node('str50', value_type=String(val_list=['HERE', 'IAM'], max_sz=7))

        middle1 = Node('middle1')
        middle1.set_subnodes_with_csts([
            3, ['u>', [nint_1_alt, 2]],
            2, ['u>', [nint_1, 1, 10], [nint_2, 2], [nstr_1, 1], [nint_3, 2], [nstr_2, 1]],
            1, ['u>', [nint_1_alt, 1], [nint_3, 1], 'u=+', [nstr_2, 1], [nint_1, 2], 'u>', [nstr_1, 1],
                'u=.', [nint_50, 1], [nint_51, 1], [nstr_50, 2, 3]]
        ])

        yeah = Node('yeah', value_type=String(val_list=['TBD', 'YEAH!'], max_sz=10, ascii_mode=True))

        splitter = Node('splitter', value_type=String(val_list=['TBD'], max_sz=10))
        splitter.set_attr(NodeInternals.Abs_Postpone)
        splitter.enforce_absorb_constraints(AbsNoCsts())

        def nint_10_helper(blob, constraints, node_internals):
            off = blob.find(b'\xd2')
            if off > -1:
                self.helper2_called = True
                return AbsorbStatus.Accept, off, None
            else:
                return AbsorbStatus.Reject, 0, None

        nint_10 = Node('nint10', value_type=UINT16_be(int_list=[0xcbbc, 0xd2d3]))
        nint_10.set_absorb_helper(nint_10_helper)
        nstr_10 = Node('str10', value_type=String(val_list=['TBD', 'THE_END'], max_sz=7))

        delim = Node('delim', value_type=String(val_list=[','], size=1))
        nint_20 = Node('nint20', value_type=INT_str(int_list=[1,2,3]))
        nint_21 = Node('nint21', value_type=UINT8(int_list=[0xbb]))
        bottom = Node('bottom', subnodes=[delim, nint_20, nint_21])

        bottom2 = Node('bottom2', base_node=bottom)

        middle2 = Node('middle2')
        middle2.set_subnodes_with_csts([
            1, ['u>', [splitter, 1], [nint_10, 1], [bottom, 0, 1], [nstr_10 ,1], [bottom2, 0, 1]]
        ])

        top = Node('top', subnodes=[middle1, yeah, middle2])
        top2 = Node('top2', base_node=top)

        top.set_env(Env())
        top2.set_env(Env())

        msg = '\xe1\xe2\xe1\xe2\xff\xeeCOOL!\xc1\xc2\x88\x9912345678YEAH!\xef\xdf\xbf\xd2\xd3,2\xbbTHE_END'

        # middle1: nint_1_alt + nint_3 + 2*nint_1 + nstr_1('ABCD') + nint_51 + 2*nstr_50 + nint_50
        msg2 = '\xff\xe2\x88\x99\xe1\xe2\xcd\xabABCD\xef\xfeIAMHERE\xbfYEAH!\xef\xdf\xbf\xd2\xd3,2\xbbTHE_END'
        
        print('\n****** top ******\n')
        status, off, size, name = top.absorb(msg)

        print('\n---[message to absorb: msg]---')
        print(repr(msg))
        print('---[absorbed message]---')
        # print(repr(top))
        print(top.get_value())

        def verif_val_and_print(arg, log_func=None):
            Node._print_contents(arg)
            if 'TBD' in arg:
                raise ValueError('Dissection Error!')

        top.show(print_contents_func=verif_val_and_print)
        l = top.get_nodes_names()

        print('\n****** top2 ******\n')
        status2, off2, size2, name2 = top2.absorb(msg2)

        print('\n---[message to absorb: msg2]---')
        print(repr(msg2))
        print('---[absorbed message]---')
        top2.show()

        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)
        self.assertEqual(len(l), 19)
        self.assertEqual(len(msg), size)
        self.assertTrue(self.helper1_called)
        self.assertTrue(self.helper2_called)
        self.assertEqual(top.get_node_by_path("top/middle2/str10").get_flatten_value(), b'THE_END')

        # Because constraints are untighten on this node, its nominal
        # size of 4 is set to 5 when absorbing b'COOL!'
        self.assertEqual(top.get_node_by_path("top/middle1/cool").get_flatten_value(), b'COOL!')
        
        self.assertEqual(status2, AbsorbStatus.FullyAbsorbed)

        del self.helper1_called
        del self.helper2_called

        print('\n*** test __getitem__() ***\n')
        print(top["top/middle2"])
        print('\n***\n')
        print(repr(top["top/middle2"]))


    def test_show(self):

        a = fmk.dm.get_external_node(dm_name='usb', data_id='DEV')
        b = fmk.dm.get_external_node(dm_name='png', data_id='PNG_00')

        a.show(raw_limit=400)
        b.show(raw_limit=400)

        b['PNG_00/chunks/chk/height']=a
        b.show(raw_limit=400)

        b['PNG_00/chunks/chk/height/idProduct']=a
        b.show(raw_limit=400)


class TestHLAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass


    def test_create_graph(self):

        a = {'name': 'top',
             'contents': [
                 {'weight': 2,
                  'contents': [
                      # block 1
                      {'section_type': MH.Ordered,
                       'duplicate_mode': MH.Copy,
                       'contents': [

                           {'contents': String(max_sz=10),
                            'name': 'val1',
                            'qty': (1, 5)},

                           {'name': 'val2'},

                           {'name': 'middle',
                            'mode': MH.NotMutableClone,
                            'contents': [{
                                'section_type': MH.Ordered,
                                'contents': [
                                    
                                    {'contents': String(val_list=['OK', 'KO'], size=2),
                                     'name': 'val2'},

                                    {'name': 'val21',
                                     'clone': 'val1'},

                                    {'name': 'USB_desc',
                                     'export_from': 'usb',
                                     'data_id': 'STR'},

                                    {'type': MH.Leaf,
                                     'contents': lambda x: x[0] + x[1],
                                     'name': 'val22',
                                     'node_args': ['val1', 'val3'],
                                     'mode': MH.FrozenArgs}
                                ]}]},

                           {'contents': String(max_sz = 10),
                            'name': 'val3',
                            'sync_qty_with': 'val1',
                            'alt': [
                                {'conf': 'alt1',
                                 'contents': SINT8(int_list=[1,4,8])},
                                {'conf': 'alt2',
                                 'contents': UINT16_be(mini=0xeeee, maxi=0xff56),
                                 'determinist': True}]}
                       ]},

                      # block 2
                      {'section_type': MH.Pick,
                       'contents': [
                           {'contents': String(val_list=['PLIP', 'PLOP'], size=4),
                            'name': ('val21', 2)},

                           {'contents': SINT16_be(int_list=[-1, -3, -5, 7]),
                            'name': ('val22', 2)}
                       ]}
                  ]}
             ]}


        mh = ModelHelper(fmk.dm)
        node = mh.create_graph_from_desc(a)
        
        node.set_env(Env())
        node.show()

        node.unfreeze_all()
        node.show()
        node.unfreeze_all()
        node.show()

        node.reset_state(recursive=True)
        node.set_current_conf('alt1', recursive=True)
        node.show()

        node.reset_state(recursive=True)
        node.set_current_conf('alt2', recursive=True)
        node.show()


        print('\nNode Dictionnary (size: {:d}):\n'.format(len(mh.node_dico)))
        for name, node in mh.node_dico.items():
            print(name, ': ', repr(node), node.c)


class TestDataModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @unittest.skipIf(not run_long_tests, "Long test case")
    def test_data_makers(self):

        for dm in fmk.dm_list:
            dm.load_data_model(fuzzer._name2dm)
            print("Test '%s' Data Model" % dm.name)
            for data_id in dm.data_identifiers():
                print("Try to get '%s'" % data_id)
                data  = dm.get_data(data_id)
                data.get_value()
                # data.show(raw_limit=200)
                print('Success!')


    @unittest.skipIf(ignore_data_model_specifics, "USB specific test cases")
    def test_usb_specifics(self):

        dm = fmk.get_data_model_by_name('usb')
        dm.build_data_model()

        msd_conf = dm.get_data('MSD_CONF')
        msd_conf.show()
        
        self.assertEqual(len(msd_conf.to_bytes()), 32)


    @unittest.skipIf(ignore_data_model_specifics, "PNG specific test cases")
    def test_png_specifics(self):

        dm = fmk.get_data_model_by_name('png')
        dm.build_data_model()

        for n, png in dm.png_dict.items():

            png_buff = png.get_flatten_value()
            png.show(raw_limit=400)

            with open('./workspace/TEST_FUZZING_' + n, 'wb') as f:
                f.write(png_buff)

            filename = os.path.join(dm.get_import_directory_path(), n)
            with open(filename, 'rb') as orig:
                orig_buff = orig.read()

            if png_buff == orig_buff:
                print("\n*** Builded Node ('%s') match the original image" % png.name)
            else:
                print("\n*** ERROR: Builded Node ('%s') does not match the original image!" % png.name)

            self.assertEqual(png_buff, orig_buff)

    @unittest.skipIf(ignore_data_model_specifics, "JPG specific test cases")
    def test_jpg_specifics(self):

        dm = fmk.get_data_model_by_name('jpg')
        dm.build_data_model()

        for n, jpg in dm.jpg_dict.items():

            jpg_buff = jpg.get_flatten_value()

            with open('./workspace/TEST_FUZZING_' + n, 'wb') as f:
                f.write(jpg_buff)

            filename = os.path.join(dm.get_import_directory_path(), n)
            with open(filename, 'rb') as orig:
                orig_buff = orig.read()

            if jpg_buff == orig_buff:
                print("\n*** Builded Node ('%s') match the original image" % jpg.name)
            else:
                print("\n*** ERROR: Builded Node ('%s') does not match the original image!" % jpg.name)

            self.assertEqual(jpg_buff, orig_buff)


    @unittest.skipIf(ignore_data_model_specifics, "ZIP specific test cases")
    def test_zip_specifics(self):

        dm = fmk.get_data_model_by_name('zip')
        dm.build_data_model()

        abszip = dm.pkzip.get_clone('ZIP')
        abszip.set_current_conf('ABS', recursive=True)

        # We generate a ZIP file from the model only (no real ZIP file)
        zip_buff = dm.get_data('ZIP').get_flatten_value()
        lg = len(zip_buff)

        # dm.pkzip.show(raw_limit=400)
        # dm.pkzip.reset_state(recursive=True)
        status, off, size, name = abszip.absorb(zip_buff, constraints=AbsNoCsts(size=True,struct=True))
        # abszip.show(raw_limit=400)

        print('\n*** Absorb Status:', status, off, size, name)
        print('*** Length of generated ZIP:', lg)

        self.assertEqual(status, AbsorbStatus.FullyAbsorbed)

        abs_buff = abszip.get_flatten_value()
        if zip_buff == abs_buff:
            print("\n*** Absorption of the generated node has worked!")
        else:
            print("\n*** ERROR: Absorption of the generated node has NOT worked!")

        self.assertEqual(zip_buff, abs_buff)

        # abszip.show()
        flen_before = len(abszip['ZIP/file_list/file/data'].to_bytes())
        print('file data len before: ', flen_before)

        off_before = abszip['ZIP/cdir/cdir_hdr:2/file_hdr_off']
        # Needed to avoid generated ZIP files that have less than 2 files.
        if off_before is not None:
            # Make modification of the ZIP and verify that some other ZIP
            # fields are automatically updated
            off_before = off_before.get_flatten_value()
            print('offset before:', off_before)
            csz_before = abszip['ZIP/file_list/file/header/common_attrs/compressed_size'].to_bytes()
            print('compressed_size before:', csz_before)

            abszip['ZIP/file_list/file/header/common_attrs/compressed_size'].set_current_conf('MAIN')

            NEWVAL = b'TEST'
            print(abszip['ZIP/file_list/file/data'].absorb(NEWVAL, constraints=AbsNoCsts()))

            flen_after = len(abszip['ZIP/file_list/file/data'].to_bytes())
            print('file data len after: ', flen_after)

            abszip.unfreeze(only_generators=True)
            abszip.get_value()

            # print('\n******\n')
            # abszip.show()

            off_after = abszip['ZIP/cdir/cdir_hdr:2/file_hdr_off'].get_flatten_value()
            print('offset after: ', off_after)
            csz_after = abszip['ZIP/file_list/file/header/common_attrs/compressed_size'].to_bytes()
            print('compressed_size after:', csz_after)

            # Should not be equal in the general case
            self.assertNotEqual(off_before, off_after)
            # Should be equal in the general case
            self.assertEqual(struct.unpack('<L', off_before)[0] - struct.unpack('<L', off_after)[0],
                             flen_before - flen_after)
            self.assertEqual(struct.unpack('<L', csz_after)[0], len(NEWVAL))


        for n, pkzip in dm.zip_dict.items():

            zip_buff = pkzip.get_flatten_value()
            # pkzip.show(raw_limit=400)

            with open('./workspace/TEST_FUZZING_' + n, 'wb') as f:
                f.write(zip_buff)

            filename = os.path.join(dm.get_import_directory_path(), n)
            with open(filename, 'rb') as orig:
                orig_buff = orig.read()
                
            err_msg = "Some ZIP are not supported (those that doesn't store compressed_size" \
                      " in the file headers)"
            if zip_buff == orig_buff:
                print("\n*** Builded Node ('%s') match the original image" % pkzip.name)
            else:
                print("\n*** ERROR: Builded Node ('%s') does not match the original image!" % pkzip.name)
                # print(err_msg)

            self.assertEqual(zip_buff, orig_buff, msg=err_msg)


class TestFMK(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fmk.enable_data_model(name='example')

    def setUp(self):
        pass

    def test_generic_disruptors_01(self):
        dmaker_type = 'TESTNODE'

        gen_disruptors = fmk._generic_tactics.get_disruptors().keys()
        print('\n-=[ GENERIC DISRUPTORS ]=-\n')
        print(gen_disruptors)

        for dis in gen_disruptors:
            print("\n\n---[ Tested Disruptor %r ]---" % dis)
            if dis == 'EXT':
                d = fmk.get_data([dmaker_type, (dis, None, UI(cmd='/bin/cat', file_mode=True))])
            else:
                d = fmk.get_data([dmaker_type, dis])
            if d is None:
                raise ValueError
            else:
                fmk.log_data(d)
                print("\n---[ Pretty Print ]---\n")
                d.pretty_print()
                fmk.cleanup_dmaker(dmaker_type=dmaker_type, reset_existing_seed=True)

        fmk.cleanup_all_dmakers(reset_existing_seed=True)


if __name__ == "__main__":

    results = collections.OrderedDict()

    fuzzer = Fuzzer()

    fuzzer.enable_data_model(name='example')
    fmk = fuzzer

    dm = example.data_model
    # dm.load_data_model(fuzzer._name2dm)

    # print(test_args, sys.argv)
    args = [sys.argv[0]] + test_args[1]

    unittest.main(verbosity=2, argv=args)




