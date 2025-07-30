// Main JavaScript for Kho Mỹ Phẩm

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc chắn muốn xóa?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-calculate totals
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const priceInputs = document.querySelectorAll('.price-input');
    const totalInputs = document.querySelectorAll('.total-input');

    function calculateTotal() {
        const quantity = parseFloat(this.value) || 0;
        const price = parseFloat(this.closest('tr').querySelector('.price-input')?.value) || 0;
        const total = quantity * price;
        this.closest('tr').querySelector('.total-input')?.value = total.toFixed(2);
    }

    quantityInputs.forEach(input => {
        input.addEventListener('input', calculateTotal);
    });

    priceInputs.forEach(input => {
        input.addEventListener('input', calculateTotal);
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Date picker enhancement
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });

    // Batch code generator
    const generateBatchCodeBtn = document.getElementById('generate-batch-code');
    if (generateBatchCodeBtn) {
        generateBatchCodeBtn.addEventListener('click', function() {
            const now = new Date();
            const batchCode = `LOT${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`;
            document.getElementById('batch-code-input').value = batchCode;
        });
    }

    // Stock level indicators
    function updateStockIndicators() {
        const stockElements = document.querySelectorAll('.stock-level');
        stockElements.forEach(element => {
            const stock = parseInt(element.dataset.stock);
            const threshold = parseInt(element.dataset.threshold) || 10;
            
            element.classList.remove('text-success', 'text-warning', 'text-danger');
            
            if (stock <= 0) {
                element.classList.add('text-danger');
                element.innerHTML += ' <i class="fas fa-exclamation-triangle"></i>';
            } else if (stock <= threshold) {
                element.classList.add('text-warning');
                element.innerHTML += ' <i class="fas fa-exclamation-circle"></i>';
            } else {
                element.classList.add('text-success');
            }
        });
    }

    updateStockIndicators();

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Export to Excel functionality
    const exportButtons = document.querySelectorAll('.btn-export');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const table = this.closest('.table-responsive').querySelector('table');
            const ws = XLSX.utils.table_to_sheet(table);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
            XLSX.writeFile(wb, "bao_cao.xlsx");
        });
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.querySelector('.loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
} 