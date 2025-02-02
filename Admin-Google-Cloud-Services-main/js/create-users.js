function showUploadCsv() {
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = `
      <h3>Upload CSV</h3>
      <p>Use the form below to upload a CSV file containing user details.</p>
      <form>
        <div class="mb-3">
          <label for="csvFile" class="form-label">Upload CSV File</label>
          <input type="file" class="form-control" id="csvFile" accept=".csv">
        </div>
        <button type="submit" class="btn btn-success">Upload</button>
      </form>
    `;
  }
  
  function showManualForm() {
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = `
      <h3>Create Users Manually</h3>
      <p>Fill out the form below to add a user manually.</p>
      <form>
        <div class="mb-3">
          <label for="firstName" class="form-label">First Name</label>
          <input type="text" class="form-control" id="firstName" placeholder="Enter first name" required>
        </div>
        <div class="mb-3">
          <label for="lastName" class="form-label">Last Name</label>
          <input type="text" class="form-control" id="lastName" placeholder="Enter last name" required>
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" placeholder="Enter email address" required>
        </div>
        <div class="mb-3">
          <label for="phone" class="form-label">Phone Number</label>
          <input type="tel" class="form-control" id="phone" placeholder="Enter phone number">
        </div>
        <button type="submit" class="btn btn-success">Create User</button>
      </form>
    `;
  }
  