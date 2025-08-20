#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据管理器
用于生成、管理和清理测试数据

使用方法:
python tests/database/test_data_manager.py --action generate --count 100
python tests/database/test_data_manager.py --action cleanup
python tests/database/test_data_manager.py --action export --output test_data.json
"""

import os
import sys
import json
import random
import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from faker import Faker

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestDataManager:
    """
    测试数据管理器
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self._get_default_db_path()
        self.connection = None
        self.fake = Faker(['zh_CN', 'en_US'])  # 支持中文和英文
        self.categories = [
            '电子产品', '服装鞋帽', '家居用品', '图书音像', 
            '运动户外', '美妆个护', '食品饮料', '母婴用品'
        ]
        self.order_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    def _get_default_db_path(self) -> str:
        """
        获取默认数据库路径
        """
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / 'data' / 'test.db')
    
    def connect(self):
        """
        连接数据库
        """
        # 确保数据库目录存在
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        # 创建表（如果不存在）
        self._create_tables()
    
    def disconnect(self):
        """
        断开数据库连接
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _create_tables(self):
        """
        创建数据库表
        """
        cursor = self.connection.cursor()
        
        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                phone VARCHAR(20),
                address TEXT,
                city VARCHAR(50),
                country VARCHAR(50),
                postal_code VARCHAR(20),
                date_of_birth DATE,
                gender VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP
            )
        """)
        
        # 商品分类表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                parent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (parent_id) REFERENCES categories (id)
            )
        """)
        
        # 商品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                cost_price DECIMAL(10, 2),
                stock_quantity INTEGER DEFAULT 0,
                min_stock_level INTEGER DEFAULT 0,
                category_id INTEGER,
                brand VARCHAR(50),
                model VARCHAR(50),
                weight DECIMAL(8, 2),
                dimensions VARCHAR(50),
                color VARCHAR(30),
                size VARCHAR(20),
                material VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                featured BOOLEAN DEFAULT 0,
                rating DECIMAL(3, 2) DEFAULT 0,
                review_count INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # 订单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                tax_amount DECIMAL(10, 2) DEFAULT 0,
                shipping_amount DECIMAL(10, 2) DEFAULT 0,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                payment_method VARCHAR(30),
                payment_status VARCHAR(20) DEFAULT 'pending',
                shipping_address TEXT,
                billing_address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                shipped_at TIMESTAMP,
                delivered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 订单项表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # 商品评论表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                title VARCHAR(200),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                helpful_count INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 购物车表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                UNIQUE(user_id, product_id)
            )
        """)
        
        self.connection.commit()
        print("📊 数据库表创建完成")
    
    def generate_users(self, count: int = 100) -> List[int]:
        """
        生成测试用户数据
        """
        print(f"👥 生成 {count} 个测试用户...")
        
        cursor = self.connection.cursor()
        user_ids = []
        
        for i in range(count):
            # 生成用户数据
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"{first_name.lower()}_{last_name.lower()}_{i}"
            email = f"{username}@{self.fake.domain_name()}"
            
            user_data = {
                'username': username,
                'email': email,
                'password_hash': self.fake.sha256(),
                'first_name': first_name,
                'last_name': last_name,
                'phone': self.fake.phone_number(),
                'address': self.fake.address(),
                'city': self.fake.city(),
                'country': self.fake.country(),
                'postal_code': self.fake.postcode(),
                'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80),
                'gender': random.choice(['male', 'female', 'other']),
                'is_active': random.choice([1, 1, 1, 0]),  # 75% 活跃用户
                'last_login': self.fake.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.2 else None
            }
            
            try:
                cursor.execute("""
                    INSERT INTO users (
                        username, email, password_hash, first_name, last_name,
                        phone, address, city, country, postal_code,
                        date_of_birth, gender, is_active, last_login
                    ) VALUES (
                        :username, :email, :password_hash, :first_name, :last_name,
                        :phone, :address, :city, :country, :postal_code,
                        :date_of_birth, :gender, :is_active, :last_login
                    )
                """, user_data)
                
                user_ids.append(cursor.lastrowid)
                
            except sqlite3.IntegrityError:
                # 如果用户名或邮箱重复，跳过
                continue
        
        self.connection.commit()
        print(f"✅ 成功生成 {len(user_ids)} 个用户")
        return user_ids
    
    def generate_categories(self) -> List[int]:
        """
        生成商品分类数据
        """
        print("📂 生成商品分类...")
        
        cursor = self.connection.cursor()
        category_ids = []
        
        for category_name in self.categories:
            cursor.execute("""
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """, (category_name, f"{category_name}相关商品"))
            
            category_ids.append(cursor.lastrowid)
        
        self.connection.commit()
        print(f"✅ 成功生成 {len(category_ids)} 个商品分类")
        return category_ids
    
    def generate_products(self, count: int = 500, category_ids: List[int] = None) -> List[int]:
        """
        生成测试商品数据
        """
        print(f"🛍️ 生成 {count} 个测试商品...")
        
        if not category_ids:
            category_ids = self.get_category_ids()
        
        cursor = self.connection.cursor()
        product_ids = []
        
        # 商品名称模板
        product_templates = {
            '电子产品': ['智能手机', '笔记本电脑', '平板电脑', '智能手表', '耳机', '充电器', '数据线'],
            '服装鞋帽': ['T恤', '牛仔裤', '连衣裙', '运动鞋', '皮鞋', '帽子', '围巾'],
            '家居用品': ['沙发', '床垫', '台灯', '花瓶', '地毯', '窗帘', '收纳盒'],
            '图书音像': ['小说', '教材', '漫画', 'CD', 'DVD', '有声书', '电子书'],
            '运动户外': ['跑步鞋', '瑜伽垫', '哑铃', '帐篷', '背包', '运动服', '护膝'],
            '美妆个护': ['面膜', '口红', '洗面奶', '护肤霜', '香水', '洗发水', '牙刷'],
            '食品饮料': ['咖啡', '茶叶', '巧克力', '饼干', '果汁', '坚果', '蜂蜜'],
            '母婴用品': ['奶粉', '尿布', '婴儿车', '玩具', '儿童服装', '奶瓶', '安全座椅']
        }
        
        brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'LG', 'Xiaomi', 'Huawei', 'Uniqlo', 'Zara']
        colors = ['黑色', '白色', '红色', '蓝色', '绿色', '黄色', '紫色', '粉色', '灰色', '棕色']
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        materials = ['棉', '聚酯纤维', '真皮', '人造革', '金属', '塑料', '玻璃', '木材']
        
        for i in range(count):
            category_id = random.choice(category_ids)
            
            # 获取分类名称
            cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
            category_name = cursor.fetchone()['name']
            
            # 根据分类生成商品名称
            if category_name in product_templates:
                base_name = random.choice(product_templates[category_name])
                brand = random.choice(brands)
                product_name = f"{brand} {base_name} {self.fake.word().title()}"
            else:
                product_name = f"{random.choice(brands)} {self.fake.word().title()}"
            
            # 生成价格（根据分类调整价格范围）
            if category_name == '电子产品':
                price = round(random.uniform(100, 5000), 2)
            elif category_name in ['服装鞋帽', '美妆个护']:
                price = round(random.uniform(20, 500), 2)
            elif category_name == '家居用品':
                price = round(random.uniform(50, 2000), 2)
            else:
                price = round(random.uniform(10, 300), 2)
            
            cost_price = round(price * random.uniform(0.4, 0.7), 2)
            
            product_data = {
                'name': product_name,
                'description': self.fake.text(max_nb_chars=200),
                'price': price,
                'cost_price': cost_price,
                'stock_quantity': random.randint(0, 1000),
                'min_stock_level': random.randint(5, 50),
                'category_id': category_id,
                'brand': random.choice(brands),
                'model': f"Model-{self.fake.bothify('??##')}",
                'weight': round(random.uniform(0.1, 50.0), 2),
                'dimensions': f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm",
                'color': random.choice(colors),
                'size': random.choice(sizes) if random.random() > 0.5 else None,
                'material': random.choice(materials),
                'is_active': random.choice([1, 1, 1, 0]),  # 75% 活跃商品
                'featured': random.choice([1, 0, 0, 0]),  # 25% 特色商品
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(0, 500)
            }
            
            cursor.execute("""
                INSERT INTO products (
                    name, description, price, cost_price, stock_quantity, min_stock_level,
                    category_id, brand, model, weight, dimensions, color, size, material,
                    is_active, featured, rating, review_count
                ) VALUES (
                    :name, :description, :price, :cost_price, :stock_quantity, :min_stock_level,
                    :category_id, :brand, :model, :weight, :dimensions, :color, :size, :material,
                    :is_active, :featured, :rating, :review_count
                )
            """, product_data)
            
            product_ids.append(cursor.lastrowid)
        
        self.connection.commit()
        print(f"✅ 成功生成 {len(product_ids)} 个商品")
        return product_ids
    
    def generate_orders(self, count: int = 200, user_ids: List[int] = None, product_ids: List[int] = None) -> List[int]:
        """
        生成测试订单数据
        """
        print(f"📦 生成 {count} 个测试订单...")
        
        if not user_ids:
            user_ids = self.get_user_ids()
        if not product_ids:
            product_ids = self.get_product_ids()
        
        cursor = self.connection.cursor()
        order_ids = []
        
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'alipay', 'wechat_pay', 'bank_transfer']
        payment_statuses = ['pending', 'completed', 'failed', 'refunded']
        
        for i in range(count):
            user_id = random.choice(user_ids)
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{i+1:06d}"
            
            # 随机选择1-5个商品
            order_products = random.sample(product_ids, random.randint(1, min(5, len(product_ids))))
            
            # 计算订单总金额
            total_amount = 0
            order_items = []
            
            for product_id in order_products:
                # 获取商品价格
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                product = cursor.fetchone()
                if not product:
                    continue
                
                quantity = random.randint(1, 5)
                unit_price = float(product['price'])
                item_total = unit_price * quantity
                discount = round(item_total * random.uniform(0, 0.2), 2)  # 0-20% 折扣
                item_total_after_discount = item_total - discount
                
                total_amount += item_total_after_discount
                
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': item_total_after_discount,
                    'discount_amount': discount
                })
            
            if not order_items:
                continue
            
            # 计算税费和运费
            tax_amount = round(total_amount * 0.1, 2)  # 10% 税费
            shipping_amount = round(random.uniform(5, 20), 2) if total_amount < 100 else 0
            discount_amount = round(total_amount * random.uniform(0, 0.1), 2)  # 订单级折扣
            
            final_total = total_amount + tax_amount + shipping_amount - discount_amount
            
            # 生成订单时间（过去30天内）
            created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
            
            order_data = {
                'user_id': user_id,
                'order_number': order_number,
                'total_amount': round(final_total, 2),
                'tax_amount': tax_amount,
                'shipping_amount': shipping_amount,
                'discount_amount': discount_amount,
                'status': random.choice(self.order_statuses),
                'payment_method': random.choice(payment_methods),
                'payment_status': random.choice(payment_statuses),
                'shipping_address': self.fake.address(),
                'billing_address': self.fake.address(),
                'notes': self.fake.text(max_nb_chars=100) if random.random() > 0.7 else None,
                'created_at': created_at
            }
            
            # 根据订单状态设置发货和送达时间
            shipped_at = None
            delivered_at = None
            
            if order_data['status'] in ['shipped', 'delivered']:
                shipped_at = created_at + timedelta(days=random.randint(1, 3))
                
                if order_data['status'] == 'delivered':
                    delivered_at = shipped_at + timedelta(days=random.randint(1, 7))
            
            order_data['shipped_at'] = shipped_at
            order_data['delivered_at'] = delivered_at
            
            # 插入订单
            cursor.execute("""
                INSERT INTO orders (
                    user_id, order_number, total_amount, tax_amount, shipping_amount, discount_amount,
                    status, payment_method, payment_status, shipping_address, billing_address,
                    notes, created_at, shipped_at, delivered_at
                ) VALUES (
                    :user_id, :order_number, :total_amount, :tax_amount, :shipping_amount, :discount_amount,
                    :status, :payment_method, :payment_status, :shipping_address, :billing_address,
                    :notes, :created_at, :shipped_at, :delivered_at
                )
            """, order_data)
            
            order_id = cursor.lastrowid
            order_ids.append(order_id)
            
            # 插入订单项
            for item in order_items:
                item['order_id'] = order_id
                cursor.execute("""
                    INSERT INTO order_items (
                        order_id, product_id, quantity, unit_price, total_price, discount_amount
                    ) VALUES (
                        :order_id, :product_id, :quantity, :unit_price, :total_price, :discount_amount
                    )
                """, item)
        
        self.connection.commit()
        print(f"✅ 成功生成 {len(order_ids)} 个订单")
        return order_ids
    
    def generate_reviews(self, count: int = 300, user_ids: List[int] = None, product_ids: List[int] = None) -> List[int]:
        """
        生成商品评论数据
        """
        print(f"⭐ 生成 {count} 个商品评论...")
        
        if not user_ids:
            user_ids = self.get_user_ids()
        if not product_ids:
            product_ids = self.get_product_ids()
        
        cursor = self.connection.cursor()
        review_ids = []
        
        review_titles = [
            "很好的产品", "质量不错", "物超所值", "推荐购买", "还可以",
            "一般般", "不太满意", "质量有问题", "非常满意", "超出预期"
        ]
        
        for i in range(count):
            user_id = random.choice(user_ids)
            product_id = random.choice(product_ids)
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]  # 偏向高评分
            
            review_data = {
                'product_id': product_id,
                'user_id': user_id,
                'rating': rating,
                'title': random.choice(review_titles),
                'content': self.fake.text(max_nb_chars=300),
                'created_at': self.fake.date_time_between(start_date='-60d', end_date='now'),
                'is_verified': random.choice([1, 1, 0]),  # 67% 验证评论
                'helpful_count': random.randint(0, 50)
            }
            
            try:
                cursor.execute("""
                    INSERT INTO product_reviews (
                        product_id, user_id, rating, title, content, created_at, is_verified, helpful_count
                    ) VALUES (
                        :product_id, :user_id, :rating, :title, :content, :created_at, :is_verified, :helpful_count
                    )
                """, review_data)
                
                review_ids.append(cursor.lastrowid)
                
            except sqlite3.IntegrityError:
                # 如果用户已经评论过该商品，跳过
                continue
        
        self.connection.commit()
        print(f"✅ 成功生成 {len(review_ids)} 个评论")
        return review_ids
    
    def generate_shopping_cart(self, user_ids: List[int] = None, product_ids: List[int] = None):
        """
        生成购物车数据
        """
        print("🛒 生成购物车数据...")
        
        if not user_ids:
            user_ids = self.get_user_ids()
        if not product_ids:
            product_ids = self.get_product_ids()
        
        cursor = self.connection.cursor()
        cart_items = 0
        
        # 为30%的用户生成购物车
        active_users = random.sample(user_ids, int(len(user_ids) * 0.3))
        
        for user_id in active_users:
            # 每个用户1-8个购物车商品
            cart_products = random.sample(product_ids, random.randint(1, min(8, len(product_ids))))
            
            for product_id in cart_products:
                cart_data = {
                    'user_id': user_id,
                    'product_id': product_id,
                    'quantity': random.randint(1, 5),
                    'added_at': self.fake.date_time_between(start_date='-7d', end_date='now')
                }
                
                try:
                    cursor.execute("""
                        INSERT INTO shopping_cart (user_id, product_id, quantity, added_at)
                        VALUES (:user_id, :product_id, :quantity, :added_at)
                    """, cart_data)
                    
                    cart_items += 1
                    
                except sqlite3.IntegrityError:
                    # 如果用户购物车中已有该商品，跳过
                    continue
        
        self.connection.commit()
        print(f"✅ 成功生成 {cart_items} 个购物车项目")
    
    def get_user_ids(self) -> List[int]:
        """
        获取所有用户ID
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE is_active = 1")
        return [row[0] for row in cursor.fetchall()]
    
    def get_category_ids(self) -> List[int]:
        """
        获取所有分类ID
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM categories WHERE is_active = 1")
        return [row[0] for row in cursor.fetchall()]
    
    def get_product_ids(self) -> List[int]:
        """
        获取所有商品ID
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM products WHERE is_active = 1")
        return [row[0] for row in cursor.fetchall()]
    
    def cleanup_all_data(self):
        """
        清理所有测试数据
        """
        print("🧹 清理所有测试数据...")
        
        cursor = self.connection.cursor()
        
        # 按依赖关系顺序删除
        tables = [
            'shopping_cart',
            'product_reviews',
            'order_items',
            'orders',
            'products',
            'categories',
            'users'
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  清理表: {table}")
        
        self.connection.commit()
        print("✅ 所有测试数据已清理")
    
    def export_data(self, output_file: str):
        """
        导出测试数据到JSON文件
        """
        print(f"📤 导出测试数据到 {output_file}...")
        
        cursor = self.connection.cursor()
        
        data = {}
        
        # 导出所有表的数据
        tables = ['users', 'categories', 'products', 'orders', 'order_items', 'product_reviews', 'shopping_cart']
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            data[table] = []
            for row in rows:
                # 将Row对象转换为字典
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # 处理日期时间类型
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[key] = value
                data[table].append(row_dict)
        
        # 添加统计信息
        data['statistics'] = {
            'users_count': len(data['users']),
            'categories_count': len(data['categories']),
            'products_count': len(data['products']),
            'orders_count': len(data['orders']),
            'order_items_count': len(data['order_items']),
            'reviews_count': len(data['product_reviews']),
            'cart_items_count': len(data['shopping_cart']),
            'export_time': datetime.now().isoformat()
        }
        
        # 写入文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据导出完成: {output_path}")
        print(f"📊 导出统计: {data['statistics']}")
    
    def import_data(self, input_file: str):
        """
        从JSON文件导入测试数据
        """
        print(f"📥 从 {input_file} 导入测试数据...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cursor = self.connection.cursor()
        
        # 按依赖关系顺序导入
        import_order = ['users', 'categories', 'products', 'orders', 'order_items', 'product_reviews', 'shopping_cart']
        
        for table in import_order:
            if table not in data:
                continue
            
            table_data = data[table]
            if not table_data:
                continue
            
            print(f"  导入表: {table} ({len(table_data)} 条记录)")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall() if col[1] != 'id']  # 排除自增ID
            
            # 构建插入语句
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # 批量插入数据
            for row in table_data:
                values = [row.get(col) for col in columns]
                try:
                    cursor.execute(insert_sql, values)
                except sqlite3.IntegrityError as e:
                    print(f"    跳过重复记录: {e}")
                    continue
        
        self.connection.commit()
        print("✅ 数据导入完成")
    
    def generate_all_data(self, users_count: int = 100, products_count: int = 500, orders_count: int = 200, reviews_count: int = 300):
        """
        生成所有类型的测试数据
        """
        print("🚀 开始生成完整的测试数据集...")
        
        # 生成分类
        category_ids = self.generate_categories()
        
        # 生成用户
        user_ids = self.generate_users(users_count)
        
        # 生成商品
        product_ids = self.generate_products(products_count, category_ids)
        
        # 生成订单
        order_ids = self.generate_orders(orders_count, user_ids, product_ids)
        
        # 生成评论
        review_ids = self.generate_reviews(reviews_count, user_ids, product_ids)
        
        # 生成购物车
        self.generate_shopping_cart(user_ids, product_ids)
        
        print("🎉 完整测试数据集生成完成！")
        print(f"📊 数据统计:")
        print(f"  - 用户: {len(user_ids)}")
        print(f"  - 分类: {len(category_ids)}")
        print(f"  - 商品: {len(product_ids)}")
        print(f"  - 订单: {len(order_ids)}")
        print(f"  - 评论: {len(review_ids)}")


def main():
    parser = argparse.ArgumentParser(description='测试数据管理器')
    parser.add_argument('--action', '-a', required=True, 
                       choices=['generate', 'cleanup', 'export', 'import', 'generate-all'],
                       help='执行的操作')
    parser.add_argument('--db-path', help='数据库文件路径')
    parser.add_argument('--count', '-c', type=int, default=100, help='生成数据的数量')
    parser.add_argument('--output', '-o', help='导出文件路径')
    parser.add_argument('--input', '-i', help='导入文件路径')
    parser.add_argument('--users', type=int, default=100, help='用户数量')
    parser.add_argument('--products', type=int, default=500, help='商品数量')
    parser.add_argument('--orders', type=int, default=200, help='订单数量')
    parser.add_argument('--reviews', type=int, default=300, help='评论数量')
    
    args = parser.parse_args()
    
    manager = TestDataManager(args.db_path)
    
    try:
        manager.connect()
        
        if args.action == 'generate':
            # 生成基础数据
            category_ids = manager.generate_categories()
            user_ids = manager.generate_users(args.count)
            product_ids = manager.generate_products(args.count, category_ids)
            
        elif args.action == 'generate-all':
            manager.generate_all_data(args.users, args.products, args.orders, args.reviews)
            
        elif args.action == 'cleanup':
            manager.cleanup_all_data()
            
        elif args.action == 'export':
            output_file = args.output or f"test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            manager.export_data(output_file)
            
        elif args.action == 'import':
            if not args.input:
                print("❌ 请指定导入文件路径 (--input)")
                return
            manager.import_data(args.input)
        
        print("✅ 操作完成！")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        raise
    finally:
        manager.disconnect()


if __name__ == '__main__':
    main()