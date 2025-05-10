// User data storage (in a real application, this would be handled by a backend server)
let users = JSON.parse(localStorage.getItem('users')) || [];
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

// Update navigation bar based on authentication status
function updateNavigation() {
    const authButtons = document.getElementById('auth-buttons');
    if (!authButtons) return;

    if (currentUser) {
        authButtons.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-gray-700">Welcome, ${currentUser.name}</span>
                <button onclick="logout()" class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">Logout</button>
            </div>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="login.html" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Login</a>
        `;
    }
}

// Handle login form submission
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const user = users.find(u => u.email === email && u.password === password);
        if (user) {
            currentUser = user;
            localStorage.setItem('currentUser', JSON.stringify(user));
            updateNavigation();
            window.location.href = 'index.html';
        } else {
            alert('Invalid email or password');
        }
    });
}

// Handle registration form submission
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        if (users.some(u => u.email === email)) {
            alert('Email already registered');
            return;
        }

        const newUser = { name, email, password };
        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));
        alert('Registration successful! Please login.');
        window.location.href = 'login.html';
    });
}

// Handle logout
function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    updateNavigation();
    window.location.href = 'index.html';
}

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
    updateNavigation();
}); 