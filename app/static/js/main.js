// 全局变量
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
let compareList = JSON.parse(localStorage.getItem('compareList')) || [];

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    updateCartBadge();
    updateWishlistBadge();
    setupEventListeners();
    initializeTooltips();
    initializeLazyLoading();
});

// 应用初始化
function initializeApp() {
    // 初始化Bootstrap组件
    if (typeof bootstrap !== 'undefined') {
        // 初始化所有tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // 初始化所有popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // 设置CSRF token
    setupCSRFToken();
    
    // 初始化页面特定功能
    const currentPage = getCurrentPage();
    switch(currentPage) {
        case 'products':
            initializeProductsPage();
            break;
        case 'product_detail':
            initializeProductDetailPage();
            break;
        case 'cart':
            initializeCartPage();
            break;
        case 'index':
            initializeHomePage();
            break;
    }
}

// 获取当前页面
function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('/products/')) return 'product_detail';
    if (path.includes('/products')) return 'products';
    if (path.includes('/cart')) return 'cart';
    if (path === '/' || path.includes('/index')) return 'index';
    return 'other';
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // 添加到购物车按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-cart') || e.target.closest('.add-to-cart')) {
            e.preventDefault();
            const button = e.target.classList.contains('add-to-cart') ? e.target : e.target.closest('.add-to-cart');
            const productId = button.dataset.productId;
            const quantity = button.dataset.quantity || 1;
            addToCart(productId, parseInt(quantity));
        }
    });
    
    // 添加到收藏夹按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-wishlist') || e.target.closest('.add-to-wishlist')) {
            e.preventDefault();
            const button = e.target.classList.contains('add-to-wishlist') ? e.target : e.target.closest('.add-to-wishlist');
            const productId = button.dataset.productId;
            toggleWishlist(productId);
        }
    });
    
    // 商品对比功能
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-compare') || e.target.closest('.add-to-compare')) {
            e.preventDefault();
            const button = e.target.classList.contains('add-to-compare') ? e.target : e.target.closest('.add-to-compare');
            const productId = button.dataset.productId;
            toggleCompare(productId);
        }
    });
    
    // 数量调整按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('quantity-btn')) {
            e.preventDefault();
            const action = e.target.dataset.action;
            const input = e.target.parentElement.querySelector('input[type="number"]');
            adjustQuantity(input, action);
        }
    });
}

// 设置CSRF Token
function setupCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
        // 设置axios默认headers
        if (typeof axios !== 'undefined') {
            axios.defaults.headers.common['X-CSRFToken'] = token.getAttribute('content');
        }
        
        // 设置fetch默认headers
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = token.getAttribute('content');
            return originalFetch(url, options);
        };
    }
}

// 购物车功能
function addToCart(productId, quantity = 1) {
    // 显示加载状态
    showLoading('正在添加到购物车...');
    
    // 发送请求到后端
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            // 更新本地购物车
            updateLocalCart(productId, quantity);
            updateCartBadge();
            showToast('商品已添加到购物车', 'success');
            
            // 添加动画效果
            animateAddToCart(productId);
        } else {
            showToast(data.message || '添加失败', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showToast('网络错误，请重试', 'error');
    });
}

// 更新本地购物车
function updateLocalCart(productId, quantity) {
    const existingItem = cart.find(item => item.product_id == productId);
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            product_id: productId,
            quantity: quantity,
            added_at: new Date().toISOString()
        });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
}

// 更新购物车徽章
function updateCartBadge() {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'flex' : 'none';
    }
}

// 收藏夹功能
function toggleWishlist(productId) {
    const index = wishlist.indexOf(productId);
    if (index > -1) {
        wishlist.splice(index, 1);
        showToast('已从收藏夹移除', 'info');
    } else {
        wishlist.push(productId);
        showToast('已添加到收藏夹', 'success');
    }
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateWishlistBadge();
    updateWishlistButtons();
}

// 更新收藏夹徽章
function updateWishlistBadge() {
    const badge = document.querySelector('.wishlist-badge');
    if (badge) {
        badge.textContent = wishlist.length;
        badge.style.display = wishlist.length > 0 ? 'flex' : 'none';
    }
}

// 更新收藏夹按钮状态
function updateWishlistButtons() {
    document.querySelectorAll('.add-to-wishlist').forEach(button => {
        const productId = button.dataset.productId;
        const icon = button.querySelector('i');
        if (wishlist.includes(productId)) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            button.classList.add('text-danger');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            button.classList.remove('text-danger');
        }
    });
}

// 商品对比功能
function toggleCompare(productId) {
    const index = compareList.indexOf(productId);
    if (index > -1) {
        compareList.splice(index, 1);
        showToast('已从对比列表移除', 'info');
    } else {
        if (compareList.length >= 4) {
            showToast('最多只能对比4个商品', 'warning');
            return;
        }
        compareList.push(productId);
        showToast('已添加到对比列表', 'success');
    }
    localStorage.setItem('compareList', JSON.stringify(compareList));
    updateCompareButtons();
}

// 更新对比按钮状态
function updateCompareButtons() {
    document.querySelectorAll('.add-to-compare').forEach(button => {
        const productId = button.dataset.productId;
        if (compareList.includes(productId)) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// 数量调整
function adjustQuantity(input, action) {
    let currentValue = parseInt(input.value) || 1;
    const min = parseInt(input.min) || 1;
    const max = parseInt(input.max) || 999;
    
    if (action === 'increase' && currentValue < max) {
        currentValue++;
    } else if (action === 'decrease' && currentValue > min) {
        currentValue--;
    }
    
    input.value = currentValue;
    
    // 触发change事件
    input.dispatchEvent(new Event('change'));
}

// 搜索处理
function handleSearch(e) {
    e.preventDefault();
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (query) {
        window.location.href = `/products?search=${encodeURIComponent(query)}`;
    }
}

// 显示提示消息
function showToast(message, type = 'info', duration = 3000) {
    // 创建toast容器（如果不存在）
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // 创建toast元素
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${getBootstrapColor(type)} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // 显示toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // 自动移除
    setTimeout(() => {
        if (toastElement && toastElement.parentNode) {
            toastElement.remove();
        }
    }, duration + 500);
}

// 获取Bootstrap颜色类
function getBootstrapColor(type) {
    const colors = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colors[type] || 'info';
}

// 获取提示图标
function getToastIcon(type) {
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    return icons[type] || 'fas fa-info-circle';
}

// 显示加载状态
function showLoading(message = '加载中...') {
    let loadingModal = document.getElementById('loading-modal');
    if (!loadingModal) {
        const modalHtml = `
            <div id="loading-modal" class="modal fade" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-sm modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body text-center py-4">
                            <div class="spinner-border text-primary mb-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div id="loading-message">${message}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        loadingModal = document.getElementById('loading-modal');
    }
    
    document.getElementById('loading-message').textContent = message;
    const modal = new bootstrap.Modal(loadingModal);
    modal.show();
}

// 隐藏加载状态
function hideLoading() {
    const loadingModal = document.getElementById('loading-modal');
    if (loadingModal) {
        const modal = bootstrap.Modal.getInstance(loadingModal);
        if (modal) {
            modal.hide();
        }
    }
}

// 添加到购物车动画
function animateAddToCart(productId) {
    const productCard = document.querySelector(`[data-product-id="${productId}"]`);
    const cartIcon = document.querySelector('.btn-cart');
    
    if (productCard && cartIcon) {
        // 创建飞行动画元素
        const flyingItem = document.createElement('div');
        flyingItem.innerHTML = '<i class="fas fa-shopping-cart"></i>';
        flyingItem.style.cssText = `
            position: fixed;
            z-index: 9999;
            color: #007bff;
            font-size: 20px;
            pointer-events: none;
            transition: all 0.8s cubic-bezier(0.2, 1, 0.3, 1);
        `;
        
        // 设置起始位置
        const productRect = productCard.getBoundingClientRect();
        const cartRect = cartIcon.getBoundingClientRect();
        
        flyingItem.style.left = productRect.left + productRect.width / 2 + 'px';
        flyingItem.style.top = productRect.top + productRect.height / 2 + 'px';
        
        document.body.appendChild(flyingItem);
        
        // 执行动画
        setTimeout(() => {
            flyingItem.style.left = cartRect.left + cartRect.width / 2 + 'px';
            flyingItem.style.top = cartRect.top + cartRect.height / 2 + 'px';
            flyingItem.style.opacity = '0';
            flyingItem.style.transform = 'scale(0.5)';
        }, 10);
        
        // 清理动画元素
        setTimeout(() => {
            flyingItem.remove();
        }, 800);
        
        // 购物车图标动画
        cartIcon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            cartIcon.style.transform = 'scale(1)';
        }, 200);
    }
}

// 初始化工具提示
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// 初始化懒加载
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// 页面特定初始化函数
function initializeHomePage() {
    // 数字动画
    animateNumbers();
    
    // 轮播图自动播放
    const carousel = document.querySelector('#heroCarousel');
    if (carousel && typeof bootstrap !== 'undefined') {
        new bootstrap.Carousel(carousel, {
            interval: 5000,
            wrap: true
        });
    }
}

function initializeProductsPage() {
    // 价格范围滑块
    initializePriceRange();
    
    // 筛选功能
    setupFilters();
    
    // 排序功能
    setupSorting();
    
    // 无限滚动
    setupInfiniteScroll();
}

function initializeProductDetailPage() {
    // 图片切换
    setupImageGallery();
    
    // 规格选择
    setupSpecSelection();
    
    // 数量选择
    setupQuantitySelection();
    
    // 标签页
    setupTabs();
}

function initializeCartPage() {
    // 购物车计算
    updateCartSummary();
    
    // 优惠券
    setupCoupons();
    
    // 批量操作
    setupBatchOperations();
}

// 数字动画
function animateNumbers() {
    const numbers = document.querySelectorAll('.stat-number');
    numbers.forEach(number => {
        const target = parseInt(number.textContent);
        let current = 0;
        const increment = target / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            number.textContent = Math.floor(current).toLocaleString();
        }, 20);
    });
}

// 价格范围滑块
function initializePriceRange() {
    const minPrice = document.getElementById('minPrice');
    const maxPrice = document.getElementById('maxPrice');
    const minPriceDisplay = document.getElementById('minPriceDisplay');
    const maxPriceDisplay = document.getElementById('maxPriceDisplay');
    
    if (minPrice && maxPrice) {
        minPrice.addEventListener('input', function() {
            if (minPriceDisplay) minPriceDisplay.textContent = this.value;
            if (parseInt(this.value) > parseInt(maxPrice.value)) {
                maxPrice.value = this.value;
                if (maxPriceDisplay) maxPriceDisplay.textContent = this.value;
            }
        });
        
        maxPrice.addEventListener('input', function() {
            if (maxPriceDisplay) maxPriceDisplay.textContent = this.value;
            if (parseInt(this.value) < parseInt(minPrice.value)) {
                minPrice.value = this.value;
                if (minPriceDisplay) minPriceDisplay.textContent = this.value;
            }
        });
    }
}

// 筛选功能
function setupFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            // 自动提交筛选
            setTimeout(() => {
                this.submit();
            }, 300);
        });
    }
}

// 排序功能
function setupSorting() {
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const url = new URL(window.location);
            url.searchParams.set('sort', this.value);
            window.location.href = url.toString();
        });
    }
}

// 无限滚动
function setupInfiniteScroll() {
    let loading = false;
    let page = 1;
    
    window.addEventListener('scroll', function() {
        if (loading) return;
        
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
            loading = true;
            loadMoreProducts();
        }
    });
    
    function loadMoreProducts() {
        // 实现加载更多商品的逻辑
        // 这里可以发送AJAX请求获取更多商品
        setTimeout(() => {
            loading = false;
            page++;
        }, 1000);
    }
}

// 图片画廊
function setupImageGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail-container');
    const mainImage = document.getElementById('mainProductImage');
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const newSrc = this.querySelector('img').src;
            if (mainImage) {
                mainImage.src = newSrc;
            }
            
            // 更新活动状态
            thumbnails.forEach(t => t.classList.remove('border-primary'));
            this.classList.add('border-primary');
        });
    });
}

// 规格选择
function setupSpecSelection() {
    const specButtons = document.querySelectorAll('.spec-option');
    
    specButtons.forEach(button => {
        button.addEventListener('click', function() {
            const specType = this.dataset.specType;
            
            // 移除同类型的其他选中状态
            document.querySelectorAll(`[data-spec-type="${specType}"]`).forEach(btn => {
                btn.classList.remove('active');
            });
            
            // 添加当前选中状态
            this.classList.add('active');
            
            // 更新价格（如果需要）
            updateProductPrice();
        });
    });
}

// 更新商品价格
function updateProductPrice() {
    // 根据选中的规格更新价格
    // 这里可以发送请求到后端获取新价格
}

// 数量选择
function setupQuantitySelection() {
    const quantityInput = document.getElementById('quantity');
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    
    quantityButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            adjustQuantity(quantityInput, action);
        });
    });
}

// 标签页
function setupTabs() {
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('data-bs-target');
            
            // 懒加载标签页内容
            if (target === '#reviews' && !document.querySelector('#reviews .reviews-loaded')) {
                loadReviews();
            }
        });
    });
}

// 加载评价
function loadReviews() {
    const reviewsContainer = document.querySelector('#reviews');
    if (reviewsContainer) {
        // 添加加载标记
        reviewsContainer.classList.add('reviews-loaded');
        
        // 这里可以发送AJAX请求加载评价数据
        showLoading('正在加载评价...');
        
        setTimeout(() => {
            hideLoading();
            // 模拟加载完成
        }, 1000);
    }
}

// 购物车摘要更新
function updateCartSummary() {
    const cartItems = document.querySelectorAll('.cart-item');
    let subtotal = 0;
    
    cartItems.forEach(item => {
        const price = parseFloat(item.dataset.price || 0);
        const quantity = parseInt(item.querySelector('.quantity-input').value || 0);
        subtotal += price * quantity;
    });
    
    // 更新小计
    const subtotalElement = document.getElementById('subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = '¥' + subtotal.toFixed(2);
    }
    
    // 计算总计（包括运费、优惠等）
    const shipping = parseFloat(document.getElementById('shipping')?.textContent.replace('¥', '') || 0);
    const discount = parseFloat(document.getElementById('discount')?.textContent.replace('¥', '') || 0);
    const total = subtotal + shipping - discount;
    
    const totalElement = document.getElementById('total');
    if (totalElement) {
        totalElement.textContent = '¥' + total.toFixed(2);
    }
}

// 优惠券设置
function setupCoupons() {
    const couponBadges = document.querySelectorAll('.coupon-badge');
    const couponInput = document.getElementById('couponCode');
    
    couponBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            const couponCode = this.dataset.couponCode;
            if (couponInput) {
                couponInput.value = couponCode;
            }
        });
    });
    
    // 应用优惠券
    const applyCouponBtn = document.getElementById('applyCoupon');
    if (applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function() {
            const code = couponInput.value.trim();
            if (code) {
                applyCoupon(code);
            }
        });
    }
}

// 应用优惠券
function applyCoupon(code) {
    showLoading('正在验证优惠券...');
    
    fetch('/api/coupon/apply', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('优惠券应用成功', 'success');
            updateCartSummary();
        } else {
            showToast(data.message || '优惠券无效', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('网络错误，请重试', 'error');
    });
}

// 批量操作
function setupBatchOperations() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const batchDeleteBtn = document.getElementById('batchDelete');
    const batchMoveBtn = document.getElementById('batchMove');
    
    // 全选/取消全选
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBatchButtons();
        });
    }
    
    // 单项选择
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBatchButtons();
        });
    });
    
    // 批量删除
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            const selectedItems = getSelectedItems();
            if (selectedItems.length > 0) {
                if (confirm(`确定要删除选中的 ${selectedItems.length} 个商品吗？`)) {
                    batchDeleteItems(selectedItems);
                }
            }
        });
    }
    
    // 批量移动到收藏夹
    if (batchMoveBtn) {
        batchMoveBtn.addEventListener('click', function() {
            const selectedItems = getSelectedItems();
            if (selectedItems.length > 0) {
                batchMoveToWishlist(selectedItems);
            }
        });
    }
}

// 更新全选状态
function updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    
    if (selectAllCheckbox && itemCheckboxes.length > 0) {
        const checkedCount = document.querySelectorAll('.item-checkbox:checked').length;
        selectAllCheckbox.checked = checkedCount === itemCheckboxes.length;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < itemCheckboxes.length;
    }
}

// 更新批量操作按钮状态
function updateBatchButtons() {
    const selectedCount = document.querySelectorAll('.item-checkbox:checked').length;
    const batchDeleteBtn = document.getElementById('batchDelete');
    const batchMoveBtn = document.getElementById('batchMove');
    
    if (batchDeleteBtn) {
        batchDeleteBtn.disabled = selectedCount === 0;
    }
    if (batchMoveBtn) {
        batchMoveBtn.disabled = selectedCount === 0;
    }
}

// 获取选中的商品
function getSelectedItems() {
    const selectedCheckboxes = document.querySelectorAll('.item-checkbox:checked');
    return Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
}

// 批量删除商品
function batchDeleteItems(itemIds) {
    showLoading('正在删除商品...');
    
    fetch('/api/cart/batch-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_ids: itemIds })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('商品删除成功', 'success');
            // 刷新页面或移除DOM元素
            location.reload();
        } else {
            showToast(data.message || '删除失败', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('网络错误，请重试', 'error');
    });
}

// 批量移动到收藏夹
function batchMoveToWishlist(itemIds) {
    showLoading('正在移动到收藏夹...');
    
    fetch('/api/cart/batch-move-to-wishlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_ids: itemIds })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('已移动到收藏夹', 'success');
            location.reload();
        } else {
            showToast(data.message || '移动失败', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('网络错误，请重试', 'error');
    });
}

// 工具函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 格式化价格
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

// 格式化日期
function formatDate(date) {
    return new Date(date).toLocaleDateString('zh-CN');
}

// 导出函数供全局使用
window.addToCart = addToCart;
window.toggleWishlist = toggleWishlist;
window.toggleCompare = toggleCompare;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.updateCartSummary = updateCartSummary;
window.applyCoupon = applyCoupon;