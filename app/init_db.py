#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库表和插入测试数据
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from faker import Faker
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, CartItem

# 创建Faker实例
fake = Faker('zh_CN')

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 删除所有表
        print("正在删除现有数据库表...")
        db.drop_all()
        
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        
        # 插入测试数据
        print("正在插入测试数据...")
        create_test_users()
        create_test_products()
        create_test_cart_items()
        
        # 提交事务
        db.session.commit()
        print("数据库初始化完成！")

def create_test_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 创建管理员用户
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        created_at=datetime.utcnow()
    )
    db.session.add(admin)
    
    # 创建普通测试用户
    test_user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('test123'),
        is_admin=False,
        created_at=datetime.utcnow()
    )
    db.session.add(test_user)
    
    # 创建更多随机用户
    for i in range(20):
        user = User(
            username=fake.user_name() + str(i),
            email=fake.email(),
            password_hash=generate_password_hash('password123'),
            is_admin=False,
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        db.session.add(user)
    
    print(f"已创建 {22} 个测试用户")

def create_test_products():
    """创建测试商品"""
    print("创建测试商品...")
    
    # 商品分类
    categories = [
        '电子产品', '服装鞋帽', '家居用品', '图书音像', 
        '运动户外', '美妆护肤', '食品饮料', '母婴用品'
    ]
    
    # 电子产品
    electronics = [
        {
            'name': 'iPhone 15 Pro',
            'description': '苹果最新旗舰手机，搭载A17 Pro芯片，支持5G网络，拍照效果出色。',
            'price': 7999.00,
            'stock': 50,
            'category': '电子产品',
            'image_url': 'https://via.placeholder.com/300x300/007bff/ffffff?text=iPhone+15+Pro'
        },
        {
            'name': 'MacBook Pro 14英寸',
            'description': '搭载M3芯片的专业级笔记本电脑，适合开发者和创意工作者。',
            'price': 14999.00,
            'stock': 30,
            'category': '电子产品',
            'image_url': 'https://via.placeholder.com/300x300/6c757d/ffffff?text=MacBook+Pro'
        },
        {
            'name': 'AirPods Pro 2',
            'description': '主动降噪无线耳机，音质出色，佩戴舒适。',
            'price': 1899.00,
            'stock': 100,
            'category': '电子产品',
            'image_url': 'https://via.placeholder.com/300x300/28a745/ffffff?text=AirPods+Pro'
        },
        {
            'name': 'iPad Air',
            'description': '轻薄便携的平板电脑，支持Apple Pencil，适合学习和工作。',
            'price': 4399.00,
            'stock': 80,
            'category': '电子产品',
            'image_url': 'https://via.placeholder.com/300x300/dc3545/ffffff?text=iPad+Air'
        },
        {
            'name': 'Apple Watch Series 9',
            'description': '智能手表，健康监测功能强大，支持多种运动模式。',
            'price': 2999.00,
            'stock': 60,
            'category': '电子产品',
            'image_url': 'https://via.placeholder.com/300x300/ffc107/000000?text=Apple+Watch'
        }
    ]
    
    # 服装鞋帽
    clothing = [
        {
            'name': 'Nike Air Max 270',
            'description': '经典运动鞋，舒适透气，适合日常穿着和运动。',
            'price': 899.00,
            'stock': 120,
            'category': '服装鞋帽',
            'image_url': 'https://via.placeholder.com/300x300/17a2b8/ffffff?text=Nike+Air+Max'
        },
        {
            'name': 'Adidas三叶草卫衣',
            'description': '经典三叶草logo卫衣，时尚百搭，面料舒适。',
            'price': 599.00,
            'stock': 200,
            'category': '服装鞋帽',
            'image_url': 'https://via.placeholder.com/300x300/343a40/ffffff?text=Adidas+卫衣'
        },
        {
            'name': 'Levi\'s 501牛仔裤',
            'description': '经典直筒牛仔裤，版型修身，质量上乘。',
            'price': 799.00,
            'stock': 150,
            'category': '服装鞋帽',
            'image_url': 'https://via.placeholder.com/300x300/6f42c1/ffffff?text=Levis+牛仔裤'
        }
    ]
    
    # 家居用品
    home_goods = [
        {
            'name': '无印良品收纳盒',
            'description': '简约设计的收纳盒，适合整理各种小物件。',
            'price': 89.00,
            'stock': 300,
            'category': '家居用品',
            'image_url': 'https://via.placeholder.com/300x300/f8f9fa/000000?text=收纳盒'
        },
        {
            'name': '宜家台灯',
            'description': '现代简约风格台灯，护眼LED光源，适合阅读和工作。',
            'price': 199.00,
            'stock': 80,
            'category': '家居用品',
            'image_url': 'https://via.placeholder.com/300x300/fd7e14/ffffff?text=台灯'
        }
    ]
    
    # 图书音像
    books = [
        {
            'name': '《Python编程：从入门到实践》',
            'description': '适合初学者的Python编程教程，内容详实，案例丰富。',
            'price': 89.00,
            'stock': 200,
            'category': '图书音像',
            'image_url': 'https://via.placeholder.com/300x300/20c997/ffffff?text=Python+编程'
        },
        {
            'name': '《软件测试的艺术》',
            'description': '软件测试领域的经典教材，适合测试工程师学习。',
            'price': 79.00,
            'stock': 150,
            'category': '图书音像',
            'image_url': 'https://via.placeholder.com/300x300/e83e8c/ffffff?text=软件测试'
        }
    ]
    
    # 合并所有商品
    all_products = electronics + clothing + home_goods + books
    
    # 添加商品到数据库
    for product_data in all_products:
        product = Product(
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            stock=product_data['stock'],
            category=product_data['category'],
            image_url=product_data['image_url'],
            created_at=fake.date_time_between(start_date='-6m', end_date='now')
        )
        db.session.add(product)
    
    # 生成更多随机商品
    for i in range(50):
        category = random.choice(categories)
        product = Product(
            name=f"{fake.word().title()} {fake.word().title()} {i+1}",
            description=fake.text(max_nb_chars=200),
            price=round(random.uniform(10.0, 5000.0), 2),
            stock=random.randint(0, 500),
            category=category,
            image_url=f'https://via.placeholder.com/300x300/{random.choice(["007bff", "28a745", "dc3545", "ffc107", "17a2b8", "6c757d"])}/ffffff?text=Product+{i+1}',
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        db.session.add(product)
    
    print(f"已创建 {len(all_products) + 50} 个测试商品")

def create_test_cart_items():
    """创建测试购物车项目"""
    print("创建测试购物车项目...")
    
    # 获取所有用户和商品
    users = User.query.all()
    products = Product.query.all()
    
    # 为部分用户创建购物车项目
    cart_items_created = 0
    for user in users[:10]:  # 只为前10个用户创建购物车
        # 随机选择1-5个商品加入购物车
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            if product.stock > 0:  # 只有有库存的商品才能加入购物车
                cart_item = CartItem(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=random.randint(1, min(3, product.stock)),
                    created_at=fake.date_time_between(start_date='-1m', end_date='now')
                )
                db.session.add(cart_item)
                cart_items_created += 1
    
    print(f"已创建 {cart_items_created} 个购物车项目")

def print_summary():
    """打印数据库摘要信息"""
    with app.app_context():
        user_count = User.query.count()
        product_count = Product.query.count()
        cart_item_count = CartItem.query.count()
        
        print("\n=== 数据库摘要 ===")
        print(f"用户数量: {user_count}")
        print(f"商品数量: {product_count}")
        print(f"购物车项目数量: {cart_item_count}")
        
        print("\n=== 测试账户信息 ===")
        print("管理员账户:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@example.com")
        
        print("\n普通用户账户:")
        print("  用户名: testuser")
        print("  密码: test123")
        print("  邮箱: test@example.com")
        
        print("\n=== 商品分类统计 ===")
        categories = db.session.query(Product.category, db.func.count(Product.id)).group_by(Product.category).all()
        for category, count in categories:
            print(f"  {category}: {count} 个商品")

def reset_database():
    """重置数据库（删除所有数据但保留表结构）"""
    with app.app_context():
        print("正在重置数据库...")
        
        # 删除所有数据
        CartItem.query.delete()
        Product.query.delete()
        User.query.delete()
        
        # 提交删除操作
        db.session.commit()
        
        print("数据库已重置")

def add_sample_data():
    """只添加示例数据（不重置数据库）"""
    with app.app_context():
        print("正在添加示例数据...")
        
        # 检查是否已有数据
        if User.query.count() > 0:
            print("数据库中已有用户数据，跳过用户创建")
        else:
            create_test_users()
        
        if Product.query.count() > 0:
            print("数据库中已有商品数据，跳过商品创建")
        else:
            create_test_products()
        
        if CartItem.query.count() > 0:
            print("数据库中已有购物车数据，跳过购物车创建")
        else:
            create_test_cart_items()
        
        db.session.commit()
        print("示例数据添加完成")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('action', choices=['init', 'reset', 'add', 'summary'], 
                       help='要执行的操作: init(初始化), reset(重置), add(添加数据), summary(显示摘要)')
    
    args = parser.parse_args()
    
    if args.action == 'init':
        init_database()
        print_summary()
    elif args.action == 'reset':
        reset_database()
    elif args.action == 'add':
        add_sample_data()
        print_summary()
    elif args.action == 'summary':
        print_summary()
    
    print("\n操作完成！")