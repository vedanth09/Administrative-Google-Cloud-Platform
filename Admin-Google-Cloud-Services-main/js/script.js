// Sidebar toggle functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    sidebar.classList.toggle('collapsed');
    content.classList.toggle('collapsed');
  }
  
  // Simulated feature actions (Placeholders for backend integration)
  function createUser() {
    alert('Create New Users feature coming soon!');
  }
  
  function generateMail() {
    alert('Generate and Send Mail feature coming soon!');
  }
  
  function deleteUser() {
    alert('Delete Users feature coming soon!');
  }
  
  function billingUsage() {
    alert('Billing & Credit Usage feature coming soon!');
  }
  
  // Login functionality
  const loginForm = document.getElementById('login-form');
  const loginPage = document.getElementById('login-page');
  const dashboardPage = document.getElementById('dashboard-page');
  
  // Check if user is already logged in
  if (localStorage.getItem('isLoggedIn') === 'true') {
    loginPage.classList.add('d-none');
    dashboardPage.classList.remove('d-none');
  }
  
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent form submission
    
    // Simulate login validation (replace this with backend validation later)
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
  
    if (email === 'admin@example.com' && password === 'admin') {
      // Save login state
      localStorage.setItem('isLoggedIn', 'true');
  
      // Show dashboard and hide login page
      loginPage.classList.add('d-none');
      dashboardPage.classList.remove('d-none');
    } else {
      alert('Invalid email or password. Please try again.');
    }
  });
  
  // Logout functionality (optional, if you have a logout button)
  function logout() {
    localStorage.removeItem('isLoggedIn');
    location.reload();
  }
  