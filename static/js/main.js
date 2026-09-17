const inputs = document.querySelectorAll("input")

inputs.forEach(inputs => {
    inputs.classList.add("form-control")

})


if (document.querySelectorAll("#flashModal")) {
    const modal = new bootstrap.Modal(document.getElementById("flashModal"));
    modal.show();
}

