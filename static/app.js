async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    if (res.ok) {
        window.location.href = "/dashboard";
    } else {
        document.getElementById("error").innerText = "Invalid credentials";
    }
}

async function logout() {
    await fetch("/logout");
    window.location.href = "/";
}

async function addBook() {
    const title = document.getElementById("title").value;
    const author = document.getElementById("author").value;
    const year = document.getElementById("year").value;
    const genre = document.getElementById("genre").value;

    await fetch("/books", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, author, year, genre })
    });

    document.getElementById("title").value = "";
    document.getElementById("author").value = "";
    document.getElementById("year").value = "";
    document.getElementById("genre").value = "";

    loadBooks();
}

async function loadBooks() {
    const res = await fetch("/books");
    const books = await res.json();

    const table = document.getElementById("books");
    table.innerHTML = "";

    books.forEach(book => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${book.title}</td>
            <td>${book.author || ""}</td>
            <td>${book.year || ""}</td>
            <td>${book.genre || ""}</td>
            <td>
                <button onclick="deleteBook(${book.id})">Delete</button>
            </td>
        `;
        table.appendChild(row);
    });
}

async function deleteBook(id) {
    await fetch(`/books/${id}`, { method: "DELETE" });
    loadBooks();
}

async function register() {
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    });

    const data = await res.json();

    if (res.ok) {
        window.location.href = "/login-page";
    } else {
        document.getElementById("error").innerText = data.error || "Registration failed";
    }
}
