var search_text="None"

// FOR GEOCODE AUTOCOMPLETE
const el = document.querySelector('ge-autocomplete')
    
// 'select' event handler - when a user selects an item from the suggestions
el.addEventListener('select', (event) => {
//     document.getElementById("place").value=event.detail;
//   console.log(event.detail)
})

// 'change' event handler - on every keystroke as the user types
el.addEventListener('change', (event) => {
 search_text=event.detail;
})

// 'features' event handler - when the GeoJSON features backing the UI change
el.addEventListener('features', (event) => {
//   console.log(event.detail)
})

// 'error' event handler - on error
el.addEventListener('error', (event) => {
  console.log(event.detail)
})

function get_list(){
    var user = {
        "search_text": search_text 
    }
    let options = {
        method: 'POST',
        body: JSON.stringify(user)
    }
    // Fake api for making post requests
    let fetchRes = fetch(
    "/search_hostels",
        options);
    fetchRes.then(res =>
        res.json()).then(d => {
            console.log(d)
        })
    }
