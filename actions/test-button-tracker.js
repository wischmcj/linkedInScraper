import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';

async function testButtonTracker() {
    console.log('🚀 Starting button click tracker test...');
    
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
        // devtools: true
    });
    const page = await browser.newPage();
    
    await page.tracing.start({path: 'trace.json'});
    // Set up comprehensive button click tracking
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        logFilePath: './test-button-clicks.log',
        trackAllElements: true, // Track all clickable elements
        captureScreenshot: false,
        screenshotDir: './test-screenshots'
    });
    
    // Navigate to a test page with various buttons
    await page.goto('https://www.google.com');
    
    console.log('📝 Now click on any buttons or links on the page...');
    console.log('📊 The tracker will log detailed information about each click');
    console.log('⏰ Waiting 30 seconds for you to interact with the page...');
    
    // Wait for user interaction
    // Wait for click events to be tracked for 30 seconds
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Get final statistics
    const stats = await getClickStatistics(page);
    console.log('\n📈 Final click statistics:', stats);

    // Stop tracking
    await stopButtonClickTracker(page);
    
    console.log('✅ Test completed! Check the console output and log file for details.');
    
    var tracing = JSON.parse(await page.tracing.stop());
    console.log(tracing);
    await browser.close();
}

// Run the test
testButtonTracker().catch(console.error); 