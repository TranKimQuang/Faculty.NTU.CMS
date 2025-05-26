document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('loginForm');
            const inputs = document.querySelectorAll('.form-control');

            // Fade-in effect on load
            const card = document.querySelector('.login-card');
            card.classList.add('fade-in');

            // Shake effect if there are flash messages (e.g., login failed)
            if (document.querySelector('.alert')) {
                card.style.animation = 'shake 0.5s ease';
                setTimeout(() => {
                    card.style.animation = '';
                }, 500);
            }

            // Hover effect for inputs
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.style.transform = 'scale(1.02)';
                });
                input.addEventListener('blur', function() {
                    this.style.transform = 'scale(1)';
                });
            });

            // Smooth submit button hover
            const button = document.querySelector('.btn-primary');
            button.addEventListener('mouseover', function() {
                this.style.transform = 'scale(1.05)';
            });
            button.addEventListener('mouseout', function() {
                this.style.transform = 'scale(1)';
            });
        });