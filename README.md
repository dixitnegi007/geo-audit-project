# Villion GEO Audit Prototype

This is my implementation for the Villion Inc. Competency Assessment. The goal was to build a mini-tool that can "look" at a website like an AI engine (ChatGPT/Perplexity) would, extract the core data, and suggest a JSON-LD schema to help that page get cited more easily.

## 🛠 How to get this running locally

I've kept the setup pretty standard so it doesn't take much time to review:

1.  **Install the basics**: 
    ```bash
    pip install -r requirements.txt
    ```
2.  **Environment Setup**: 
    Check the `.env.example` file. If you want to see the "smart" schema generation in action, rename it to `.env` and drop in an OpenAI API key. If not, the code will just fallback to a rule-based logic I wrote.
3.  **Fire it up**: 
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    You can hit the UI directly at `http://127.0.0.1:8000/`.

---

## 🧠 The Thinking Process (How I built this)

When I started this, I had to make a few quick calls on the tech stack. Here’s why I chose what I did:

### 1. Scraping: Why BeautifulSoup (and not Playwright)?
For a prototype like this, speed is everything. BeautifulSoup is incredibly fast for pulling `<title>`, `meta`, and `<h1>` tags from the initial HTML. I thought about using Playwright to handle heavy JavaScript sites, but for a "Mini Audit," BS4 is 10x lighter. If this were a production tool for Villion, I’d probably move the scraping to a worker-based Playwright cluster to handle SPAs (Single Page Apps).

### 2. The AI Part: Rule-based vs. LLM
I went with a **Hybrid approach**. 
*   **The boring stuff**: Extracting headings and images is deterministic. I don't need an expensive LLM to tell me what the H1 tag says. 
*   **The smart stuff**: I used GPT-3.5 to decide *which* Schema.org type to use (Article vs. Product vs. Organization). Rule-based systems are brittle—they fail if a "Product" page is written like a "Blog." An LLM "reads" the intent, which is crucial for GEO (Generative Engine Optimization).

### 3. Architecture for 50+ Pages (Scaling)
If I had to audit a whole site instead of one URL, I’d redesign this as follows:
*   **Background Jobs**: No one wants to wait for 50 pages to scrape in a single request. I'd use **Celery with Redis** to process audits asynchronously. The user would get a "Task ID" and we’d notify them when it’s done.
*   **Concurrency**: I'd use `httpx` or `asyncio` to fire off multiple requests at once. 
*   **Vector Search**: To truly help Villion's clients, I'd index the whole site into a **Vector DB**. This way, the LLM can see "The Big Picture" and suggest site-wide structured data, not just isolated page blocks.

---

## ⚠️ Honesty Corner: Known Weaknesses
*   **JS-Heavy Sites**: Since I’m using BS4, if a site is a pure React app with no Server-Side Rendering (SSR), the scraper will come back empty. 
*   **Image Quality**: Right now, I just grab the first image or the OG tag. I’m not checking if the image is actually high-res or relevant for a citation.
*   **CSS**: The frontend is a single HTML file with basic CSS. It’s functional for a demo, but obviously needs a proper Tailwind or Next.js setup for a real SaaS product.

---

## 📽 Walkthrough Plan
In the 5-minute video, I'll walk you through:
1.  **A live run**: Auditing a real site (like `example.com` or a news site).
2.  **The Code**: Showing how the FastAPI endpoint talks to the Scraper and the AI Generator.
3.  **The Strategy**: Talking about why the LLM is only used where it adds real value (classification) and not for simple data fetching.
