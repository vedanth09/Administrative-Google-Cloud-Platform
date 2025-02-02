// Function to delete all expired students
function deleteAllExpired() {
    alert('Deleting all students whose tenure has expired...');
    // Backend logic for deletion will go here
  }
  
  // Function to delete selected students
  function deleteSelected() {
    const selectedUsers = [];
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
  
    checkboxes.forEach((checkbox) => {
      selectedUsers.push(checkbox.dataset.userId);
    });
  
    if (selectedUsers.length > 0) {
      alert(`Deleting selected users: ${selectedUsers.join(', ')}`);
      // Backend logic for deleting selected users will go here
    } else {
      alert('No users selected for deletion.');
    }
  }
  