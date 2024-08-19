function toggleForm(blogId) {

    var form = document.getElementById('edit-form-' + blogId);
    var editButton = document.getElementById('show-edit-' + blogId);

    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        editButton.innerHTML = 'Cancel';
    } else {
        form.style.display = 'none';
        editButton.innerHTML = 'Edit';
    }
}