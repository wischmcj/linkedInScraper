import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';
import { signIn } from './apply.js';
import { manualDebug, selectorExists } from './utils.js';

import { data_automation_id_to_action } from './information.js';


async function clickEasyApplyButton(page) {

    console.log('Clicking Apply button');
    var apply_button = null;
    try {   
        apply_button = await page.$eval('button[id="jobs-apply-button-id"]', ((element) => {
            console.log(element);
            element.click();
            return element;
        }));
        console.log('Apply button found: ')
    }
    catch (error) {
        console.log('Error-1 clicking button: ', error);
        var apply_button = await page.locator('button[id="jobs-apply-button-id"]', {timeout: 5000}).click();
    }
    if (apply_button) {
        return apply_button;
    }
    else {
        console.log('Error clicking easy apply button: button not found');
        return null;
    }
}

async function fillDropdownByPartialId(partial_id,value) {
    // Gets input element whos id value contains the partial_id 
    await page.evaluate((partial_id, value) => {
        const el = document.querySelector(`[id*="${partial_id}"]`);
        console.log(el);
        if (el) {
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }, partial_id, value);
}

async function fillInputByPartialId(partialId, value) {
    const x = await page.locator(`[id*="${partialId}"]`).click();
    console.log(x);
    await page.keyboard.type(value, { delay: 100 });
    await page.keyboard.press('Enter');
}


async function answerQuestions(page) {
    // A diff version of findEasyApplyInputs that relies on
    // Already having a list of questions and answers (a different format for data_automation_id_to_action)
    let length = Object.keys(data_automation_id_to_action).length;
    for (let step = 0; step< length; step++) {
        try {
            const question = `div[data-automation-id="${data_automation_id_to_action[step][0]}"]`;
            const answer = data_automation_id_to_action[step][1]
            console.log(`Answering question ${step}: ${question}, answer: ${answer}`);

            await page.locator(`${question} button`).click();
            await page.keyboard.type(answer, { delay: 100 });
            await page.keyboard.press('Enter');
            await new Promise(r => setTimeout(r, 200));

        } catch (error) {
            console.error(error);
            console.log(`Error answering question ${step}`);
        }
    }
    await page.locator(nextButton).click();
}

async function findEasyApplyInputs(page) {
    // In easyApply modals, input fields  are nested in divs w class 
    //  XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl, which are nested in divs w class jobs-easy-apply-modal__content

    // The below collects:
    //  the 'for' attr of the label elements under these divs (functions as a question id)
    //  the text of the label elements (functions as the question text)
    var dirSelector = '[class*="XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl"]'
    const questionInfo = await page.$$eval(`${dirSelector} label`, 
                                        els => els.map(el => [el.getAttribute("for"), el.textContent]));
    var value = null                                        
    for (let [questionId, questionText] of questionInfo) {
        console.log(`Question: ${questionId}, ${questionText}`);
        // data_automation_id_to_action is a map: questionID -> answer
        value = data_automation_id_to_action[questionId][1]
        if (questionId.includes("multipleChoice")) {
            // Multiple choice questions have select + option elements in place of input
            const answerEles = await page.$$eval(`${dirSelector} select`, 
                                            els => els.map(el => el.id));
            fillDropdownByPartialId(questionId, value);
        }
        else if (questionId.includes("single-line-text")) {
            // Free text input field
            const answerEles = await page.$$eval(`${dirSelector} input`, 
                                            els => els.map(el => el.id));
            fillInputByPartialId(questionId, value);
        }
    }
    // Get and log all question data 
    ////// TO DO ///////
    var apply_button = null;
    try {   
        apply_button = await page.$eval('button[id="jobs-apply-button-id"]', ((element) => {
            console.log(element);
            element.click();
            return element;
        }));
        console.log('Apply button found: ')
    }
    catch (error) {
        console.log('Error-1 clicking button: ', error);
        var apply_button = await page.locator('button[id="jobs-apply-button-id"]', {timeout: 5000}).click();

    }
    var apply_button = null;
    try {   
        apply_button = await page.$eval('button[id="jobs-apply-button-id"]', ((element) => {
            console.log(element);
            element.click();
            return element;
        }));
        console.log('Apply button found: ')
    }
    catch (error) {
        console.log('Error-1 clicking button: ', error);
        var apply_button = await page.locator('button[id="jobs-apply-button-id"]', {timeout: 5000}).click();

    }

    for (let answer of answerEles) {
        console.log(`Answer: ${answer}`);
    }
    return {questionEles, answerEles};
}

async function testButtonTracker() {
    console.log('🚀 Starting button click tracker test...');
    
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
        slowMo: 50,
        devtools: true
    });
    const page = await browser.newPage();
    
    // await page.tracing.start({path: 'trace.json'});
    // Set up comprehensive button click tracking
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        logFilePath: './test-button-clicks.log',
        trackAllElements: true, // Track all clickable elements
        captureScreenshot: false,
        screenshotDir: './test-screenshots'
    });
    
    console.log('📝 Now click on any buttons or links on the page...');
    console.log('📊 The tracker will log detailed information about each click');
    console.log('⏰ Waiting 30 seconds for you to interact with the page...');
    

    // await new Promise(resolve => setTimeout(resolve, 5000));
    await signIn(page);

    console.log('Navigating to page');
    // Navigate to a test page with various buttons
    await page.goto('https://www.linkedin.com/jobs/view/4257497407/');

    // debugger;
    await clickEasyApplyButton(page);
    // click on the apply button
    manualDebug(page);

    var inputType='Dropdown';
    var id = 'phoneNumber-country';
    var value = 'United States (+1)';
    
    for (let i = 0; i < 1; i++) {
        try {
            var next_button = 'button[data-easy-apply-next-button=""]'
            var review_button = 'button[data-live-test-easy-apply-review-button=""]'
            if (await selectorExists(page, next_button)) {
                console.log("Next button found. Clicking");
                await page.locator(next_button).click();
            }
            else if (await selectorExists(page, review_button)) {
                console.log("Review button found. Clicking");
                await page.locator(review_button).click();
            }
            //keep looping and filling
            i=i-1;
        }
        catch (error) {
            console.log('Error clicking next button: ', error);
        }
        await new Promise(resolve => setTimeout(resolve, 5000));
    }


    // Get final statistics
    const stats = await getClickStatistics(page);
    console.log('\n📈 Final click statistics:', stats);

    // Stop tracking
    // await stopButtonClickTracker(page);
    
    console.log('✅ Test completed! Check the console output and log file for details.');
    
    // await browser.close();
}

// Run the test
testButtonTracker()
// .catch(console.error); 