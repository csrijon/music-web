const searchbtn = document.querySelector(".search-button");
const searchinput = document.querySelector(".search-input");
const container = document.querySelector(".song");
const songcards = document.querySelectorAll(".songcard")
const pesudo = document.querySelector("#pesudo-player");
const playPauseButton = document.querySelector("#onclick");
const footerimg = document.querySelector("#footer-img")
const tracktittle = document.querySelector(".track-title");
const skipnext = document.querySelector("#skip-next");
const duration = document.querySelector(".duration");
const Arrow = document.querySelector("#Arrow");
const leftimage = document.querySelector("#leftimage");
const pagraph = document.querySelector("#pa-graph");
const airname = document.querySelector("#air-name");
const homes = document.querySelector(".home");
const progressbar = document.querySelector(".progress-bar");
const progressBarContainer = document.querySelector('.progress-bar-container');
const currenttime = document.querySelector('.current-time');
const leftside = document.querySelector("#logo");
const skipprevious = document.querySelector("#skip-previous");
const trackart = document.querySelector(".track-art");
const loadingspin = document.querySelector(".loading-wave")
const upnext = document.querySelector(".up-next");
const left = document.querySelector(".left");
const upnextsec = document.querySelector(".upnextsec") ;
let currentsong = null;
let queue = [];
let queueIndex = 0;

document.addEventListener("DOMContentLoaded", async () => {
    displaySongs(await fetchGlobalSongs());
});

upnext.addEventListener("click", () => {
    if (queue[queueIndex]) {
        if (upnextsec.style.display === "none" || upnextsec.style.display === "" ) {
        upnextsec.style.transition= "all 1s ease-in-out";
        upnextsec.style.display = "block"
        setTimeout(() => {
            playNextsong();
        }, 10);
        }else{
            upnextsec.style.transition= "all 1s ease-out";
            upnextsec.style.display = "none"
            setTimeout(() => {
                playNextsong(homes)
            }, 10);
        }}else{
            alert("No songs in the queue")
        }
 })


searchinput.addEventListener("keypress",async (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        const searchsong = searchinput.value.trim();
        if (searchsong !== "") { //different value and type
            loadingspin.style.display = "flex";
            const data = await fetchSonglist(searchsong);
            loadingspin.style.display = "none";
        if (data){
            displaySongs(data);
        }}
}
 });

pesudo.addEventListener("timeupdate", () => {
    updateCurrentTime();
    updateProgress();
})
skipnext.addEventListener("click", () => {
    updateSkipNext();
})
skipprevious.addEventListener("click", () => {
    updateSkipPrevious();
})

function displaySongs(data) {
    container.innerHTML = '';
    if (!data) {
        return;
    }
    data.forEach((song) => {
        container.appendChild(generateSongCard(song));
    });
}
function generateSongCard(song) {
    const div = document.createElement("div");
    div.classList.add("songcard");
    div.innerHTML = `
        <img src="${`/cdn/thumbnail/${song.thumb_signature}`}" alt="${song.title}" class="track-cover">
        <div class="song-info">
            <p class="song-title">${song.title}</p>
            <p class="artist-name">${song.singer}</p>
        </div>
`;

    // Generate song card
    div.addEventListener("click", async () => {
        try {
            pesudo.src = `/cdn/audio/${song.media_signature}`;
            currentsong = song;
            await pesudo.play();
            queue = [];
            resp = await fetch(`/api/search/related/${currentsong.id}/${currentsong.language}`);
            data = await resp.json();
            queue = data
            queueIndex = 0;
            updateIcon();
            updateImage();
            updateText();
            updateDuration();
            playNextsong();
            
        } catch (error) {
            console.error("Error playing song:", error);
        }
    });
    return div;
}
playPauseButton.addEventListener("click", async () => {
    if (currentsong) {
        if (pesudo.paused) {
            try {
                await pesudo.play();
                console.log("Audio is now playing");
            } catch (error) {
                console.error("Error playing audio:", error);
            }
            updateIcon();
        } else {
            try {
                pesudo.pause();
                updateIcon();
                console.log("Audio is now paused");
            } catch (error) {
                console.error("Error pausing audio:", error);
            }
        }
    //    updateIcon();
    } else {
        console.log("No song selected");
    }
});
function updateIcon() {
    if (pesudo.paused) {
        playPauseButton.innerHTML = '<span class="material-symbols-outlined">play_arrow</span>';
    } 
   else{
        playPauseButton.innerHTML = '<span class="material-symbols-outlined">pause</span>';
    }
}
function updateImage() {
    if (currentsong) {
        footerimg.src = `/cdn/thumbnail/${currentsong.thumb_signature}`;
        leftimage.src = `/cdn/thumbnail/${currentsong.thumb_signature}`;
        leftside.src = `/cdn/thumbnail/${currentsong.thumb_signature}`;
        if (leftside.src) {
            leftside.style.backgroundImage = `url(${leftside.src})`;
            leftside.style.backgroundRepeat = "no-repeat";
            leftside.style.backgroundSize = "cover";
            leftside.style.backgroundPosition = "center";
            leftside.style.backdropFilter = "blur(60px)"

        }
        if (footerimg.style.display === "none") {
            footerimg.style.display = "block";
        }
        if (leftimage.style.display === "none") {
            leftimage.style.display = "block";
        }
    }
}
function updateText() {
    if (currentsong) {
        tracktittle.textContent = currentsong.title;
        pagraph.textContent = currentsong.title;
        airname.textContent = currentsong.singer
        trackart.textContent = currentsong.singer
        if (tracktittle.style.display = "none") {
            tracktittle.style.display = "block"
        } else {
            tracktittle.style.display = "none"
        }
    }
}
function updateDuration() {
    if (currentsong) {
        const time = currentsong.duration;
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        duration.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}
function updateSkipNext() {
    if (queueIndex < queue.length + 1) { 
        queueIndex += 1;  
        currentsong = queue[queueIndex]; 
        pesudo.src = `/cdn/audio/${currentsong.media_signature}`; 
        if (pesudo.src) {
            pesudo.play();
            updateImage();    
            updateText();      
            updateDuration();  
        }
    } else {
        console.log("No more songs in the queue.");  // Show a message when there are no more songs
    }
}

function updateSkipPrevious() {
    const cards = document.querySelectorAll('.songcard');
    if (currentsong&& queueIndex > 0) {
        currentsong = queue[queueIndex - 1]
        queueIndex -= 1
        pesudo.src = `/cdn/audio/${currentsong.media_signature}`;
        if (pesudo.src) {
            pesudo.play()
            updateImage();
            updateText();
            updateDuration();
            }
    }else{
        console.log("bhai gana khatam")
    }
}
function updateCurrentTime() {
    if (pesudo.currentTime) {
        const currentTime = pesudo.currentTime;
        const minutes = Math.floor(currentTime / 60);
        const seconds = Math.floor(currentTime % 60);
        currenttime.innerHTML = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
}
function updateProgress() {
    progressbar.value = pesudo.currentTime;
    progressbar.max = pesudo.duration;
    progressbar.style.width = `${updateCurrentTime(progressbar.value)/updateCurrentTime(progressbar.max) * 100}%`;
}
progressbar.addEventListener("input", () => {
    pesudo.currentTime = progressbar.value;
    updateProgress(pesudo)
})
Arrow.addEventListener("click", () => {
    const topplayer = document.querySelector(".top-player");
    if (topplayer.style.top === "44%") {
        topplayer.style.top = "139%";
        setTimeout(() => {
            Arrow.innerHTML = '<span id="Arrow" class="material-symbols-outlined">arrow_drop_down</span>'
            topplayer.style.display = "none";
        }, 1000);

    } else {
        topplayer.style.display = "block";
        topplayer.style.transition = "all 1s ease-in";
        setTimeout(() => {
            topplayer.style.top = "44%";
            Arrow.innerHTML = '<span class="material-symbols-outlined">arrow_drop_up</span>'
        }, 10);
    }
});

function playNextsong() {
    if (currentsong) {
        currentsong = queue[queueIndex]
            homes.innerHTML = "";
            upnextsec.innerHTML = "";
        queue.forEach((musiccard,index) => { // queue array r vitore protek ta element ke print korbe
            const cardElement = document.createElement("div");
            cardElement.classList.add("musiccard");
           cardElement.innerHTML = `
        <img src="${`/cdn/thumbnail/${musiccard.thumb_signature}`}" alt="${musiccard.title}">
        <div class="card-info">
            <h3>${musiccard.title}</h3>
           <p class="artist-name">${musiccard.singer}</p>
        </div>`;
        if(upnextsec.style.display ===  "block"){
            upnextsec.appendChild(cardElement);
        }else{
            homes.appendChild(cardElement)
        }
     cardElement.addEventListener("click", () => {
        currentsong = queue[index]; 
        pesudo.src = `/cdn/audio/${currentsong.media_signature}`; 
        pesudo.play();
        updateIcon(); 
        updateImage();
        updateText();
        queueIndex++
})}
)}}
pesudo.addEventListener("ended", (event) => {
    updateSkipNext();
 });

