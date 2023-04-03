function scrape(message, sender) {
    var table = document.querySelector(".record-list-table")
    var rows = table.querySelectorAll('tr')
    var header_fields = rows[0].querySelectorAll('th')
    var header = []
    for (const field of header_fields) {
        header.push(field.textContent);
        console.log(field.textContent);
    }
    var data = []
    for (const row of rows) {
        var cells = row.querySelectorAll('td')
        var person = {}
        var i = 0
        for (const cell of cells) {
            person[header[i]] = cell.textContent
            i++
        }
        if (Object.keys(person).length > 0) {
            data.push(person)
        }
    }
    navigator.clipboard.writeText(JSON.stringify(data))
    return data
}

browser.runtime.onMessage.addListener(() => {
    scrape()
    return Promise.resolve({response: ""})
})

