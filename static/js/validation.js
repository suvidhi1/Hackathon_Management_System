function validateHackathonForm() {
    const startDate = new Date(document.getElementById("start_date").value);
    const endDate = new Date(document.getElementById("end_date").value);

    if (endDate < startDate) {
        alert("End date cannot be earlier than the start date.");
        return false;
    }
    return true;
}

function openEditForm(hackathonId) {
    document.getElementById("editForm").style.display = "block";
    document.getElementById("editHackathonForm").action = `/update_hackathon/${hackathonId}`;
    // Populate fields dynamically (use AJAX or template rendering)
}
