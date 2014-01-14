# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
import time

ACC_NUMBER = "BE38733040385372"


class test_regex_account_completion(common.TransactionCase):

    def prepare(self):
        self.account_bank_statement_obj = self.registry("account.bank.statement")
        self.account_bank_statement_line_obj = self.registry("account.bank.statement.line")
        self.account_id = self.ref('account.a_expense')
        # create the completion rule
        rule_vals = {'function_to_call': 'set_account',
                     'regex': '^My statement',
                     'account_id': self.account_id}
        self.completion_rule_id = self.registry("account.statement.completion.rule").create(self.cr, self.uid, rule_vals)

        # Create the profile
        self.journal_id = self.ref("account.bank_journal")
        self.profile_id = self.registry("account.statement.profile").create(self.cr, self.uid, {
            "name": "TEST",
            "commission_account_id": self.ref("account.a_recv"),
            "journal_id": self.journal_id,
            "rule_ids": [(6, 0, [self.completion_rule_id])]})

        # Create a bank statement
        self.statement_id = self.account_bank_statement_obj.create(self.cr, self.uid, {
            "balance_end_real": 0.0,
            "balance_start": 0.0,
            "date": time.strftime('%Y-%m-%d'),
            "journal_id": self.journal_id,
            "profile_id": self.profile_id
        })

        # Create two bank statement lines
        self.statement_line1_id = self.account_bank_statement_line_obj.create(self.cr, self.uid, {
            'amount': 1000.0,
            'name': 'My statement',
            'ref': 'My ref',
            'statement_id': self.statement_id,
            'partner_acc_number': ACC_NUMBER
        })

        self.statement_line2_id = self.account_bank_statement_line_obj.create(self.cr, self.uid, {
            'amount': 2000.0,
            'name': 'My second statement',
            'ref': 'My second ref',
            'statement_id': self.statement_id,
            'partner_acc_number': ACC_NUMBER
        })

    def test_00(self):
        """Test the automatic completion on account
        """
        self.prepare()
        statement_line = self.account_bank_statement_line_obj.browse(self.cr, self.uid, self.statement_line_id)
        # before import, the
        self.assertFalse(statement_line.partner_id, "Partner_id must be blank before completion")
        statement_obj = self.account_bank_statement_obj.browse(self.cr, self.uid, self.statement_id)
        statement_obj.button_auto_completion()
        statement_line = self.account_bank_statement_line_obj.browse(self.cr, self.uid, self.statement_line_id)
        self.assertEquals(self.partner_id, statement_line.partner_id['id'], "Missing expected partner id after completion")
