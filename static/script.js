const apiBase = "http://127.0.0.1:5000";

function api(path){
    const uid = window.currentUserId;

    if(!uid){
        console.warn("Usuário não definido ainda")
    }
    const sep = path.includes("?")?"&":"?";
    return `${apiBase}${path}${sep}user_id=${encodeURIComponent(uid)}`;
}

function showSection(sectionId){
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"))
    document.getElementById(sectionId).classList.add("active")

    if(sectionId === "home") getMovie()
    if(sectionId === "liked") loadLikedMovies()
    if(sectionId === "popular") loadPopularMovies()
    if(sectionId === "recommended") loadRecommendedMovies()
    if(sectionId === "didntwatch") loadUnwatchedMovies()
        
    
}

function getMovie(){
    fetch (api("/movies"))
    //user_id = dtyyF38hpoQdDc5HCHKGrLpbfSb2
    .then(response => response.json())
    .then(data =>{
        const movie = data.data;
        const posterEl = document.getElementById("poster");

        posterEl.onerror = function() {
        // evita loop infinito caso a fallback falhe também
        posterEl.onerror = null;
        posterEl.src = "/static/no_image.png";
      };

        posterEl.src = (movie.poster_link && movie.poster_link.trim()) ? movie.poster_link : "/static/no_image.png";
        document.getElementById("title").innerText = movie.original_title
        document.getElementById("subtitle").innerText = `${movie.release_date.split("-")[0]} | ${movie.duration} min`
        document.getElementById("rating").innerText = "⭐".repeat(Math.round(movie.rating))
    })
    .catch(error => console.log(error))
}

function likeMovie(){
  fetch(api("/like"))
    .then(res => res.json())
    .then(data => {
      saveUserData("liked", data.movie);
      getMovie();
    });
}
function dislikeMovie(){
  fetch(api("/dislike"))
    .then(res => res.json())
    .then(data => {
      saveUserData("disliked", data.movie);
      getMovie();
    })
}
function skipMovie(){
  fetch(api("/did_not_watch"))
    .then(res => res.json())
    .then(data => {
      saveUserData("skipped", data.movie);
      getMovie();
    })
}


function loadLikedMovies(){
    fetch(api("/liked"))
    .then(res => res.json())
    .then(data => renderMovieList(data.data, "liked-list" ))
}

function loadPopularMovies(){
    fetch(api("/popular_movies"))
    .then(res => res.json())
    .then(data => renderMovieList(data.data, "popular-list" ))
}

function loadRecommendedMovies(){
    fetch(api("/recommended_movies"))
    .then(res => res.json())
    .then(data => renderMovieList(data.data, "recommended-list" ))
}
function loadUnwatchedMovies(){
    fetch(api("/didntwatch"))
    .then(res => res.json())
    .then(data => renderMovieList(data.data, "didntwatch-list" ))
}

function saveUserData(type, movie){
    const uid = window.currentUserId;
  const db = firebase.firestore();

  db.collection("users").doc(uid).update({
    [type]: firebase.firestore.FieldValue.arrayUnion(movie)
  }).catch(() => {
    // se o documento ainda não existe, cria
    db.collection("users").doc(uid).set({
      liked: [],
      disliked: [],
      skipped: []
    }).then(() => saveUserData(type, movie));
  });
}

function renderMovieList(movies, containerId){
    const container = document.getElementById(containerId)
    container.innerHTML = ""

    if(!movies || movies.length === 0){
        container.innerHTML = "<p>Nenhum filme encontrado</p>"
    }
    if(containerId = "liked_list"){
        movies = movies.slice().reverse()
    }

movies.forEach(m => {
    const card = document.createElement("div");
    card.className = "movie-card";
    card.innerHTML = `
      <img 
        src="${m.poster_link}" 
        alt="${m.original_title}" 
        onerror="this.onerror=null; this.src='/static/no_image.png';"
      >
      <h4>${m.original_title}</h4>
      <p>${m.release_date.split("-")[0]} | ${m.duration} min</p>
      <p>⭐ ${m.rating.toFixed(1)}</p>
    `;
    container.appendChild(card);
  });
}

//getMovie()