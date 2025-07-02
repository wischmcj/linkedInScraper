import { DuckDBInstance } from '@duckdb/node-api';
import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';

const instance = await DuckDBInstance.create('linkedin.duckdb');
const conn = await instance.connect();

const jobs = await conn.runAndReadAll('select * from linkedin_data.job_urls');
const rows = jobs.getRows();
 
console.log(rows.slice(0, 10))

const num_jobs = 5
const test = rows.slice(0, num_jobs)
const apply_button = 'button[id="jobs-apply-button-id"]';
// const job_url = "https://leidos.wd5.myworkdayjobs.com/en-US/External/job/Geospatial-Data-Scientist_R-00160099?bid=56&tid=x_de4204c6-7a43-47bd-a8e0-fd5e04bf08bb&source=APPLICANT_SOURCE-3-10317"

async function selectorExists(page, selector, timeout=1000) {
    try {
        await page.waitForSelector(selector, { timeout: timeout });
    } catch (error) {
        return false;
    }
    return true;
}
 
async function apply(job_url) {
    console.log(job_url);
    console.log('hello');
    var page = await getPage();
    console.log(typeof page)
    
    // Set up button click tracking with comprehensive logging
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        logFilePath: './button-clicks.log',
        trackAllElements: true, // Track all clickable elements, not just buttons
        captureScreenshot: false, // Set to true if you want screenshots
        screenshotDir: './click-screenshots'
    });
    
    page.on('request', request => {
        console.log(request.url());
        console.log(request.headers());
    });
    
    await page.goto(job_url);

    const all_buttons = await page.locator('::-p-xpath(//button)');
    console.log(all_buttons);
    
    await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    
    // Now when you click buttons, they will be automatically tracked
    // For example, if you click the apply button:
    // await click_apply_button(page);
    
    // Get statistics after some interactions
    const stats = await getClickStatistics(page);
    console.log('Click statistics:', stats);
    
    // Stop tracking when done
    await stopButtonClickTracker(page);
}

async function getPage() {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
    });
    const page = await browser.newPage();
    return page;
}
        

// Example of how the tracking works with manual clicks
async function demonstrateTracking(url) {
    const page = await getPage();
    
    // Set up tracking
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        trackAllElements: true
    });
    
    
    // Navigate to a test page
    await page.goto(url);
    
    // Click some elements - these will be automatically tracked
    // await page.click('a'); // This click will be logged with detailed information
    
    // Wait a bit for any async operations
    await selectorExists(page, 'button[id="Element-doesnt-exist"]', 10000);
    
    // Get statistics
    const stats = await getClickStatistics(page);
    console.log('Final statistics:', stats);
    
    // Stop tracking
    await stopButtonClickTracker(page);
    
    await page.browser().close();
}

// Run the example
// demonstrateTracking();
const job_url = 'https://www.linkedin.com/jobs/view/4253333502'

// Or run your existing apply function
// apply(job_url); 

demonstrateTracking(job_url);