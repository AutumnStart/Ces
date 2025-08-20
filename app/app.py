# -*- coding: utf-8 -*-
"""
Flask Web应用 - 测试目标应用
这是一个简单的电商网站，包含用户注册、登录、商品浏览、购物车等功能
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据库模型
class User(db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class Product(db.Model):
    """商品模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }

class CartItem(db.Model):
    """购物车项目模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product': self.product.to_dict() if self.product else None,
            'created_at': self.created_at.isoformat()
        }

# 路由定义
@app.route('/')
def index():
    """首页"""
    products = Product.query.limit(6).all()
    return render_template('index.html', products=products)

@app.route('/products')
def products():
    """商品列表页"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         current_category=category,
                         search_term=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """商品详情页"""
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 验证输入
        if not username or not email or not password:
            flash('所有字段都是必填的', 'error')
            return render_template('register.html')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """购物车页面"""
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('login'))
    
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

# API路由
@app.route('/api/products', methods=['GET'])
def api_products():
    """获取商品列表API"""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_product_detail(product_id):
    """获取商品详情API"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/cart', methods=['GET'])
def api_cart():
    """获取购物车API"""
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    return jsonify([item.to_dict() for item in cart_items])

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    """添加商品到购物车API"""
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'error': '商品ID不能为空'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    
    # 检查库存
    if product.stock < quantity:
        return jsonify({'error': '库存不足'}), 400
    
    # 检查购物车中是否已有该商品
    cart_item = CartItem.query.filter_by(
        user_id=session['user_id'], 
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'message': '添加成功', 'cart_item': cart_item.to_dict()})

@app.route('/api/users', methods=['GET'])
def api_users():
    """获取用户列表API（仅管理员）"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': '权限不足'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/health', methods=['GET'])
def api_health():
    """健康检查API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# 初始化数据库和示例数据
def init_db():
    """初始化数据库"""
    db.create_all()
    
    # 创建管理员用户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
    
    # 创建测试用户
    if not User.query.filter_by(username='testuser').first():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
    
    # 创建示例商品
    if Product.query.count() == 0:
        products = [
            Product(name='iPhone 15', description='最新款iPhone', price=7999.0, stock=50, category='手机'),
            Product(name='MacBook Pro', description='专业笔记本电脑', price=15999.0, stock=30, category='电脑'),
            Product(name='AirPods Pro', description='无线降噪耳机', price=1999.0, stock=100, category='配件'),
            Product(name='iPad Air', description='轻薄平板电脑', price=4599.0, stock=40, category='平板'),
            Product(name='Apple Watch', description='智能手表', price=2999.0, stock=60, category='手表'),
            Product(name='Magic Keyboard', description='无线键盘', price=899.0, stock=80, category='配件'),
        ]
        
        for product in products:
            db.session.add(product)
    
    db.session.commit()
    print('数据库初始化完成！')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)