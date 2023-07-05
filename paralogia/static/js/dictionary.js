function containsAllAscii(str) {
    return /^[\000-\177]*$/.test(str);
}

async function dictionarySearch(search, destinyDiv) {
    await fetch('http://127.0.0.1:5000/dictionaryLookup?search=' + search)
        .then(response => response.json())
        .then(json => {

            document.getElementById(destinyDiv).innerHTML += '<div id="spinner" class="spinner-border mt-5" rule="status"></div>';


            console.log(json['en_ja_results'])
            console.log(json['ja_en_results'])

            if (!json['en_ja_results'] && !json['ja_en_results']) {
                document.getElementById(destinyDiv).innerHTML += '<div style="margin-top: 20px">No results.</div>';
            }


            const dictionarySearchResults = document.createElement('div');

            for (let key in json['en_ja_results']) {

                const wordSpan = document.createElement('div');
                wordSpan.setAttribute('style', 'margin-top:20px');

                let entry;
                if (key == 'null') {
                    entry = document.createTextNode(search);
                } else {
                    entry = document.createTextNode(key);
                }
                wordSpan.appendChild(entry);

                const lineBreak = document.createElement('br');
                wordSpan.appendChild(lineBreak);

                const translation = document.createTextNode(json['en_ja_results'][key])
                wordSpan.appendChild(translation);

                dictionarySearchResults.appendChild(wordSpan);
            }

            for (let key in json['ja_en_results']) {

                const wordSpan = document.createElement('div');
                wordSpan.setAttribute('style', 'margin-top:20px');

                const translation = document.createTextNode(json['ja_en_results'][key])
                wordSpan.appendChild(translation);

                dictionarySearchResults.appendChild(wordSpan);
            }


            const examplesLimit = 2000;
            let totalExamplesShown = 0;
            if (!containsAllAscii(search) && Object.keys(json['ja_en_results']).length > 0) {
                
                let amountOfExamplesFound = Object.keys(json['exampleSentences']).length;
                if (amountOfExamplesFound > examplesLimit) {
                    amountOfExamplesFound = examplesLimit;
                }
                const examplesHeader = document.createElement('h3');
                const examplesHeaderText = document.createTextNode('例文 (' + amountOfExamplesFound + ' 件)');
                examplesHeader.appendChild(examplesHeaderText);
                examplesHeader.setAttribute('class', 'mt-5')

                const line = document.createElement('hr');

                dictionarySearchResults.appendChild(examplesHeader);
                dictionarySearchResults.appendChild(line);

                for (let key in json['exampleSentences']) {
                    if (totalExamplesShown == examplesLimit) {
                        break;
                    }

                    const wordSpan = document.createElement('div');
                    wordSpan.setAttribute('style', 'margin-top:20px');

                    const entry = document.createTextNode(key);
                    wordSpan.appendChild(entry);

                    const lineBreak = document.createElement('br');
                    wordSpan.appendChild(lineBreak);

                    const translation = document.createTextNode(json['exampleSentences'][key]);
                    wordSpan.appendChild(translation);

                    dictionarySearchResults.appendChild(wordSpan);
                    totalExamplesShown++;
                }
            }
            document.getElementById('spinner').remove();
            document.getElementById(destinyDiv).innerHTML += dictionarySearchResults.innerHTML;
        });
}
