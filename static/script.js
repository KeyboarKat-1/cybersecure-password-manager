function togglePassword(id, password) {

    let passwordField = document.getElementById("password-" + id);

    if (passwordField.innerText === "********") {

        passwordField.innerText = password;

    } else {

        passwordField.innerText = "********";
    }
}