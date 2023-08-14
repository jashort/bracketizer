/*
 * Timestamps are sent in UTC. This looks for elements on the page with the class
 * "timestamp" and replaces the text in it with the local time
 */
function convertUTCDateToLocalDate(date) {
    const dateUtc = new Date(date);
    const dateLocal = new Date(dateUtc.getTime() - dateUtc.getTimezoneOffset() * 60 * 1000)
    return dateLocal.toLocaleString()
}

document.addEventListener("DOMContentLoaded", function(event) {
    let timestamps = document.getElementsByClassName("timestamp");
    for (const t of timestamps) {
        t.textContent = convertUTCDateToLocalDate(t.textContent);
    }
});