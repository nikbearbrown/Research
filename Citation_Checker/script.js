    function cleanDOI(doi) {
            // Remove common prefixes
            doi = doi.trim();
            doi = doi.replace(/^https?:\/\/doi\.org\//, '');
            doi = doi.replace(/^https?:\/\/dx\.doi\.org\//, '');
            doi = doi.replace(/^doi:/, '');
            return doi;
        }

        function setDOI(doi) {
            document.getElementById('doiInput').value = doi;
            validateDOI();
        }

        async function validateDOI() {
            const doiInput = document.getElementById('doiInput');
            const doi = cleanDOI(doiInput.value);
            
            if (!doi) {
                alert('Please enter a DOI');
                return;
            }

            const submitButton = document.getElementById('submitButton');
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');

            // Show loading state
            submitButton.disabled = true;
            loading.style.display = 'block';
            resultDiv.style.display = 'none';

            try {
                const response = await fetch(`https://api.crossref.org/works/${doi}`);
                
                if (response.status === 404) {
                    showError('DOI not found in CrossRef database');
                } else if (!response.ok) {
                    showError(`Error: ${response.status} ${response.statusText}`);
                } else {
                    const data = await response.json();
                    showResult(data.message, doi);
                }
            } catch (error) {
                showError('Network error: Unable to connect to CrossRef API');
            } finally {
                submitButton.disabled = false;
                loading.style.display = 'none';
            }
        }

        function showError(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `
                <h2>❌ Not Found</h2>
                <p>${message}</p>
            `;
            resultDiv.style.display = 'block';
        }

        function showResult(publication, doi) {
            const resultDiv = document.getElementById('result');
            
            // Extract information
            const title = extractTitle(publication);
            const authors = extractAuthors(publication);
            const date = extractDate(publication);
            const journal = extractJournal(publication);
            const type = publication.type || 'unknown';
            const publisher = publication.publisher || 'N/A';
            const volume = publication.volume || '';
            const issue = publication.issue || '';
            const pages = publication.page || '';
            const citations = publication['is-referenced-by-count'] || 0;
            const url = `https://doi.org/${doi}`;

            // Format citation
            const citation = formatCitation(authors, date.year, title, journal, volume, pages, doi);

            // Build HTML
            let html = `
                <h2>✅ Publication Found</h2>
                <div class="result-item">
                    <span class="result-label">Type:</span> ${type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <div class="result-item">
                    <span class="result-label">Title:</span> ${title}
                </div>
                <div class="result-item">
                    <span class="result-label">Authors:</span> ${authors.slice(0, 3).map(a => a.full_name).join(', ')}${authors.length > 3 ? ' et al.' : ''}
                    ${authors.length > 3 ? `<div class="authors-list"><small>(and ${authors.length - 3} more authors)</small></div>` : ''}
                </div>
                <div class="result-item">
                    <span class="result-label">Published:</span> ${date.formatted}
                </div>
                <div class="result-item">
                    <span class="result-label">Journal:</span> ${journal || 'N/A'}
                </div>
                ${volume ? `<div class="result-item">
                    <span class="result-label">Volume/Issue:</span> ${volume}${issue ? `(${issue})` : ''}${pages ? `, pp. ${pages}` : ''}
                </div>` : ''}
                <div class="result-item">
                    <span class="result-label">Publisher:</span> ${publisher}
                </div>
                <div class="result-item">
                    <span class="result-label">Citations:</span> ${citations.toLocaleString()}
                </div>
                <div class="result-item">
                    <span class="result-label">URL:</span> <a href="${url}" target="_blank" class="url-link">${url}</a>
                </div>
                
                <div class="citation-box">
                    <strong>Formatted Citation:</strong><br>
                    <span id="citationText">${citation}</span>
                    <br>
                    <button class="copy-button" onclick="copyCitation()">Copy Citation</button>
                </div>
            `;

            resultDiv.className = 'result success';
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }

        function extractTitle(publication) {
            const title = publication.title;
            if (Array.isArray(title) && title.length > 0) {
                return title[0];
            } else if (typeof title === 'string') {
                return title;
            }
            return 'No title available';
        }

        function extractAuthors(publication) {
            const authors = [];
            const authorList = publication.author || [];
            
            for (const author of authorList) {
                authors.push({
                    given_name: author.given || '',
                    family_name: author.family || '',
                    full_name: `${author.given || ''} ${author.family || ''}`.trim()
                });
            }
            
            return authors;
        }

        function extractDate(publication) {
            const dateInfo = {};
            
            // Try different date fields
            for (const dateType of ['published-print', 'published-online', 'published', 'created']) {
                if (publication[dateType]) {
                    const dateParts = publication[dateType]['date-parts'];
                    if (dateParts && dateParts[0]) {
                        const parts = dateParts[0];
                        dateInfo.year = parts[0] || null;
                        dateInfo.month = parts[1] || null;
                        dateInfo.day = parts[2] || null;
                        break;
                    }
                }
            }
            
            // Format date string
            if (dateInfo.year) {
                let formatted = String(dateInfo.year);
                if (dateInfo.month) {
                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    formatted = `${months[dateInfo.month - 1]} ${dateInfo.year}`;
                }
                dateInfo.formatted = formatted;
            } else {
                dateInfo.formatted = 'Date not available';
            }
            
            return dateInfo;
        }

        function extractJournal(publication) {
            const container = publication['container-title'];
            if (Array.isArray(container) && container.length > 0) {
                return container[0];
            } else if (typeof container === 'string') {
                return container;
            }
            return '';
        }

        function formatCitation(authors, year, title, journal, volume, pages, doi) {
            let authorStr = '';
            if (authors.length > 3) {
                authorStr = `${authors[0].family_name}, ${authors[0].given_name.charAt(0)}. et al.`;
            } else {
                authorStr = authors.map(a => `${a.family_name}, ${a.given_name.charAt(0)}.`).join(', ');
            }
            
            let citation = `${authorStr} (${year || 'n.d.'}). ${title}. `;
            if (journal) {
                citation += `${journal}`;
                if (volume) {
                    citation += `, ${volume}`;
                }
                if (pages) {
                    citation += `, ${pages}`;
                }
                citation += '. ';
            }
            citation += `https://doi.org/${doi}`;
            
            return citation;
        }

        function copyCitation() {
            const citationText = document.getElementById('citationText').innerText;
            navigator.clipboard.writeText(citationText).then(() => {
                const button = event.target;
                const originalText = button.innerText;
                button.innerText = 'Copied!';
                setTimeout(() => {
                    button.innerText = originalText;
                }, 2000);
            });
        }