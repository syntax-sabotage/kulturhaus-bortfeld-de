# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.tools import html2plaintext


@tagged('post_install', '-at_install')
class TestGroupMentions(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test users
        self.user_admin = self.env.ref('base.user_admin')
        self.user_demo = self.env.ref('base.user_demo')
        
        # Create additional test users
        self.user_board_1 = self.env['res.users'].create({
            'name': 'Board Member 1',
            'login': 'board1',
            'email': 'board1@test.com',
        })
        self.user_board_2 = self.env['res.users'].create({
            'name': 'Board Member 2', 
            'login': 'board2',
            'email': 'board2@test.com',
        })
        
        # Set board member function
        self.user_board_1.partner_id.function = 'Vorstand'
        self.user_board_2.partner_id.function = 'Vorstand'
        
        # Create test project
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
        })
        
        # Create test task
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
        })
        
        # Add followers
        self.task.message_subscribe(partner_ids=[
            self.user_admin.partner_id.id,
            self.user_demo.partner_id.id,
            self.user_board_1.partner_id.id,
            self.user_board_2.partner_id.id,
        ])
    
    def test_extract_all_mention(self):
        """Test @all mention extraction"""
        body = '<p>Hello @all, please review this task</p>'
        mentions = self.task._extract_group_mentions(body)
        
        self.assertTrue(mentions['has_all'])
        self.assertFalse(mentions['has_vorstand'])
    
    def test_extract_vorstand_mention(self):
        """Test @Vorstand mention extraction"""
        body = '<p>@Vorstand approval needed</p>'
        mentions = self.task._extract_group_mentions(body)
        
        self.assertFalse(mentions['has_all'])
        self.assertTrue(mentions['has_vorstand'])
    
    def test_extract_both_mentions(self):
        """Test both @all and @Vorstand mentions"""
        body = '<p>@all FYI, @Vorstand please approve</p>'
        mentions = self.task._extract_group_mentions(body)
        
        self.assertTrue(mentions['has_all'])
        self.assertTrue(mentions['has_vorstand'])
    
    def test_compute_board_members(self):
        """Test board member computation"""
        self.task._compute_board_members()
        
        board_members = self.task.board_member_ids
        self.assertEqual(len(board_members), 2)
        self.assertIn(self.user_board_1.partner_id, board_members)
        self.assertIn(self.user_board_2.partner_id, board_members)
    
    def test_message_post_with_all_mention(self):
        """Test posting message with @all mention"""
        with self.assertLogs('odoo.addons.task_group_mentions', level='INFO') as log:
            message = self.task.message_post(
                body='<p>@all Important update</p>',
                message_type='comment',
            )
        
        # Check that all followers were notified
        self.assertIn('@all mention detected', str(log.output))
        self.assertIn('4 followers', str(log.output))  # All 4 followers
    
    def test_message_post_with_vorstand_mention(self):
        """Test posting message with @Vorstand mention"""
        with self.assertLogs('odoo.addons.task_group_mentions', level='INFO') as log:
            message = self.task.message_post(
                body='<p>@Vorstand Please review</p>',
                message_type='comment',
            )
        
        # Check that board members were notified
        self.assertIn('@Vorstand mention detected', str(log.output))
        self.assertIn('2 board members', str(log.output))  # Only 2 board members
    
    def test_action_notify_all_followers(self):
        """Test manual notification to all followers"""
        result = self.task.action_notify_all_followers()
        
        # Should return a notification action
        self.assertEqual(result.get('type'), 'ir.actions.client')
        self.assertEqual(result.get('tag'), 'display_notification')
        self.assertIn('4 followers', result['params']['message'])
    
    def test_action_notify_board_members(self):
        """Test manual notification to board members"""
        result = self.task.action_notify_board_members()
        
        # Should return a notification action
        self.assertEqual(result.get('type'), 'ir.actions.client')
        self.assertEqual(result.get('tag'), 'display_notification')
        self.assertIn('2 board members', result['params']['message'])
    
    def test_no_followers_warning(self):
        """Test warning when no followers exist"""
        # Remove all followers
        self.task.message_unsubscribe(partner_ids=self.task.message_follower_ids.mapped('partner_id').ids)
        
        result = self.task.action_notify_all_followers()
        
        # Should return a warning
        self.assertIn('warning', result)
        self.assertEqual(result['warning']['title'], 'No Followers')
    
    def test_no_board_members_warning(self):
        """Test warning when no board members exist"""
        # Remove board member functions
        self.user_board_1.partner_id.function = False
        self.user_board_2.partner_id.function = False
        self.task._compute_board_members()
        
        result = self.task.action_notify_board_members()
        
        # Should return a warning
        self.assertIn('warning', result)
        self.assertEqual(result['warning']['title'], 'No Board Members')
    
    def test_visual_badge_replacement(self):
        """Test that mentions are replaced with visual badges"""
        message = self.task.message_post(
            body='<p>@all please note, @Vorstand needs to approve</p>',
            message_type='comment',
        )
        
        # Check that badges were added
        self.assertIn('o_mail_mention_all', message.body)
        self.assertIn('o_mail_mention_vorstand', message.body)
        self.assertIn('badge', message.body)