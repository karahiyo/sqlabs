# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Yusuke Kishita <yuusuuke.kishiita@gmail.com>
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
# Original by: http://code.google.com/p/django-mptt/
from gluon import *
from gluon.storage import Storage

class MPTTModel(object):
    
    def __init__(self, db):
        self.db = db        
        
        settings = self.settings = Storage()
        settings.table_tree_name = 'node'
        settings.table_tree = None
        
    def define_tables(self, migrate = True, fake_migrate = False):
        db, settings = self.db, self.settings
        
        settings.table_tree = db.define_table(
                                              settings.table_tree_name, 
                                              Field('title'),
                                              Field('parent_id', 'integer'),
                                              Field('tree_id', 'integer'),
                                              Field('level', 'integer'), 
                                              Field('left', 'integer'), 
                                              Field('right', 'integer'),
                                              #Field('value', 'integer'), 
                                              migrate = migrate, 
                                              fake_migrate = fake_migrate)
        
#    def get_raw_field_value(self, node_id, *fields):
#        db, table_tree = self.db, self.settings.table_tree
#        node = db(table_tree.id == node_id).select().first()
#        if not node:
#            raise ValueError
#        return db(table_tree.id == node.id).select(*fields)
        
#    def set_raw_field_value(self, node_id, value, *fields):
#        db, table_tree = self.db, self.settings.table_tree
#        node = db(table_tree.id == node_id).select().first()
#        if not node:
#            raise ValueError
#        node.value = value
#        return

    def get_ancestors(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        """print get_ancestors('3', table_tree.title)"""
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left < node.left)(table_tree.right > node.right).select(orderby=table_tree.left, *fields)
    
    def get_descendants(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        """print get_descendants('2', table_tree.title)"""
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left > node.left)(table_tree.right < node.right).select(orderby=table_tree.left, *fields)
    
    def get_descendant_count(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return (node.right - node.left - 1) / 2,   
    
    def get_leafnodes(self, *fields):
        db, table_tree = self.db, self.settings.table_tree
        return db(table_tree.right == table_tree.left+1).select(orderby=table_tree.left, *fields)
    
    def get_next_sibling(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.left == node.right + 1).select(orderby=table_tree.title, *fields)
    
    def get_previous_sibling(self, node_id, *fields):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        return db(table_tree.right == node.left - 1).select(orderby=table_tree.title, *fields)
    
    def get_root(self):
        db, table_tree = self.db, self.settings.table_tree
        root = db(table_tree.left == 1).select().first()
        if not root:
            raise ValueError
        return db(table_tree.left == 1).select()
    
    def is_child_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(table_tree.id == node_id)(table_tree.left > 1).select().first():
            return True
        else:
            return False
        
    def is_leaf_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        if db(table_tree.id == node_id)(table_tree.right == table_tree.left+1).select().first():
            return True
        else:
            return False
        
    def is_root_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError        
        if db(table_tree.id == node_id)(table_tree.left == 1).select().first():
            return True
        else:
            return False
        
    def is_ancestor_of(self, node1_id, node2_id):
        db, table_tree = self.db, self.settings.table_tree
        node1 = db(table_tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(table_tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left < node2.left) and (node1.right > node2.right): 
            return True
        else:
            return False
        
    def is_descendant_of(self, node1_id, node2_id):
        db, table_tree = self.db, self.settings.table_tree
        node1 = db(table_tree.id == node1_id).select().first()
        if not node1:
            raise ValueError
        node2 = db(table_tree.id == node2_id).select().first()
        if not node1:
            raise ValueError
        if (node1.left > node2.left) and (node1.right < node2.right): 
            return True
        else:
            return False
        
    def add_node(self, node_id, target_id, position='last-child'):
        db, table_tree = self.db, self.settings.table_tree
        target = db(table_tree.id == target_id).select().first()
        if not target:
            raise ValueError
        self._update_tree(node_id, target_id, position)
        return
        
    def _update_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        target = db(table_tree.id == target_id).select().first()
        if position == 'last-child':
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + 2)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + 2)
            table_tree.insert(id=node_id, parent_id=target_id, tree_id=target.tree_id, 
                              level=target.level+1, left=target.right, right=target.right + 1)
        else:
            raise ValueError
    
    def delete_node(self, node_id):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
        db(table_tree.right >= node.right).update(right=table_tree.right - 2)
        db(table_tree.left >= node.right).update(left=table_tree.left - 2)
        db(table_tree.id == node_id).delete()
        
############################ tree_manager #########################################

    def _get_next_tree_id(self):
        db, table_tree = self.db, self.settings.table_tree
        max_tid = db().select(table_tree.ALL,orderby=~table_tree.tree_id).first()
        return max_tid.id + 1
            
    #単一ノードもしくは、あるツリーのルートノードがnode_id
    def insert_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        if not node:
            self._update_tree(node_id, target_id, position)
            return
        
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        tree_width = right - left + 1

        if target is None:
            next_tid = self._get_next_tree_id()
            if next_tid:
                table_tree.insert(id=node_id,parent_id=None,tree_id=next_tid,
                                  level=0,left=1,right=2)
            # if there is no trees
            else:
                table_tree.insert(id=node_id,parent_id=None,tree_id=1,
                                  level=0,left=1,right=2)
            return

        # root node の　兄弟を作る
        elif self.is_root_node(target.id) and position in ['left', 'right']:
            if position == 'left':
                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width + 1)
                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width + 1)
            else:
                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width + 1)
                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width + 1)
                #続きを書く  新しいルートの作成
        
        else:
            if position == 'last-child':
                #calculate  サブツリー以外への影響 　last-child
                node.update_recode(parent_id=target.id)
                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
                db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
            elif position == 'first-child':
                #calculate  サブツリー以外への影響 　first-child                           
                node.update_recode(parent_id=target.id)
                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
                db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
            elif position == 'left':
                #calculate  サブツリー以外への影響 　sibling-left
                node.update_recode(parent_id=target.parent_id)
                db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
                db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
            elif position == 'right':
                #calculate  サブツリー以外への影響 　sibling-right
                node.update_recode(parent_id=target.parent_id)
                db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
                db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
            else:
                raise ValueError
            
            #calculate  サブツリー内への影響
            for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
                beta_node.update_record(level=beta_node.level + target.level + 1,
                                        left=beta_node.left + target.right - 1,
                                        right=beta_node.right + target.right - 1,
                                        tree_id=target.tree_id)
                
    
    def _calculate_inter_tree_move_values(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        left = node.left
        right = node.right
        level = node.level
        target_right = target.right
        target_left = target.left
        
        
        
    def move_node(self, node_id, target_id, position='last-child'):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        if not node:
            raise ValueError
                
        if target is None:
            if self.is_child_node(node_id):
                self._make_child_root_node(node_id)
        elif self.is_root_node(target_id) and position in ['left','right']:
            self._make_sibling_of_root_node(node_id, target_id, position)
        else:
            if self.is_root_node(node_id):
                self._move_root_node(node_id, target_id, position)
            else:
                self._move_child_node(node_id, target_id, position)
                
    def _make_child_root_node(self, node_id, new_tree_id=None):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        if not node:
            raise ValueError
                
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        new_tree_id = self._get_next_tree_id()
                
        tree_width = right - left + 1
        node.update_recode(parent_id=None)
        
        #サブツリー内部
        for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - node.level,
                                    left=beta_node.left - (node.left - 1),
                                    right=beta_node.right - (node.left - 1),
                                    tree_id=new_tree_id)
        
        #オリジナルツリー内部 
        for alpha_node in db(table_tree.left > node.left)(table_tree.tree_id == current_tree_id).select():
            alpha_node.update_record(left=alpha_node.left - tree_width)
                    
        for alpha_node in db(table_tree.right > node.right)(table_tree.tree_id == current_tree_id).select():
            alpha_node.update_record(right=alpha_node.right - tree_width)

    def _make_sibling_of_root_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
    def _move_child_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        node_tree_id = node.id
        target_tree_id = target.id
        
        if node_tree_id == target_tree_id:
            self._move_child_within_tree(node_id, target_id, position)
        else:
            self._move_child_to_new_tree(node_id, target_id, position)
            
    def _move_child_to_new_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        new_tree_id = target.tree_id
                        
        tree_width = right - left + 1
        
        if position == 'last-child':
            #calculate  サブツリー以外への影響 　last-child
            node.update_recode(parent_id=target.id)
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'first-child':
            #calculate  サブツリー以外への影響 　first-child                           
            node.update_recode(parent_id=target.id)
            db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'left':
            #calculate  サブツリー以外への影響 　sibling-left
            node.update_recode(parent_id=target.parent_id)
            db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'right':
            #calculate  サブツリー以外への影響 　sibling-right
            node.update_recode(parent_id=target.parent_id)
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        else:
            raise ValueError

        #サブツリー内部
        for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - node.level,
                                    left=beta_node.left - (node.left - 1),
                                    right=beta_node.right - (node.left - 1),
                                    tree_id=new_tree_id)
            
        #オリジナルツリー内部 
        for alpha_node in db(table_tree.left > node.left)(table_tree.tree_id == current_tree_id).select():
            alpha_node.update_record(left=alpha_node.left - tree_width)
                    
        for alpha_node in db(table_tree.right > node.right)(table_tree.tree_id == current_tree_id).select():
            alpha_node.update_record(right=alpha_node.right - tree_width)
            
    def _move_child_within_tree(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        tree_width = right - left + 1
        target_left = target.left
        target_right = target.right
        target_level = target.level
        
        if position == 'last-child' or position == 'first-child':
            if node == target:
                raise ValueError
            elif left < target_left < right:
                raise ValueError
            if position == 'last-child':
                if target_right > right:
                    new_left = target_right - tree_width
                    new_right = target_right - 1
                else:
                    new_left = target_right
                    new_right = target_right + tree_width - 1
            else: #if position == 'first-child'
                if target_left > left:
                    new_left = target_left - tree_width + 1
                    new_right = target_left
                else:
                    new_left = target_left + 1
                    new_right = target_left + tree_width
            level_change = level - target_level - 1
            parent = target
        elif position == 'left' or position == 'right':
            if node == target:
                raise ValueError
            elif left < target_left < right:
                raise ValueError
            if position == 'left':
                if target_left > left:
                    new_left = target_left - tree_width
                    new_right = target_left - 1
                else:
                    new_left = target_left
                    new_right = target_left + tree_width - 1
            else:
                if target_right > right:
                    new_left = target_right - tree_width + 1
                    new_right = target_right
                else:
                    new_left = target_right + 1
                    new_right = target_right + tree_width
            level_change = level - target_level
            parent = target.parent_id
        else:
            raise ValueError
        
        left_boundary = min(left, new_left)
        right_boundary = max(right, new_right)
        left_right_change = new_left - left
        gap_size = tree_width
        if left_right_change > 0:
            gap_size = -gap_size
        
        #calculate  サブツリー内への影響
        for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level - level_change,
                                    left=beta_node.left + target.right - 1,
                                    right=beta_node.right + target.right - 1,
                                    tree_id=target.tree_id)
        
    def _move_root_node(self, node_id, target_id, position):
        db, table_tree = self.db, self.settings.table_tree
        node = db(table_tree.id == node_id).select().first()
        target = db(table_tree.id == target_id).select().first()
        if not node:
            raise ValueError
        
        left = node.left
        right = node.right
        level = node.level
        current_tree_id = node.tree_id
        new_tree_id = target.tree_id
        tree_width = right - left + 1
        
        if node == target:
            raise ValueError
        elif current_tree_id == new_tree_id:
            raise ValueError
        
        if position == 'last-child':
            #calculate  サブツリー以外への影響 　last-child
            node.update_recode(parent_id=target.id)
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'first-child':
            #calculate  サブツリー以外への影響 　first-child                           
            node.update_recode(parent_id=target.id)
            db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'left':
            #calculate  サブツリー以外への影響 　sibling-left
            node.update_recode(parent_id=target.parent_id)
            db(table_tree.right >= target.left)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.left)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        elif position == 'right':
            #calculate  サブツリー以外への影響 　sibling-right
            node.update_recode(parent_id=target.parent_id)
            db(table_tree.right >= target.right)(table_tree.tree_id == target.tree_id).update(right=table_tree.right + tree_width)
            db(table_tree.left >= target.right)(table_tree.tree_id == target.tree_id).update(left=table_tree.left + tree_width)
        else:
            raise ValueError
        
        #calculate  サブツリー内への影響
        for beta_node in db(table_tree.left >= node.left)(table_tree.left <= node.right)(table_tree.tree_id == current_tree_id).select():
            beta_node.update_record(level=beta_node.level + target.level + 1,
                                    left=beta_node.left + target.right - 1,
                                    right=beta_node.right + target.right - 1,
                                    tree_id=target.tree_id)
                