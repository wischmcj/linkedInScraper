
import TwoCaptcha from "@2captcha/captcha-solver"

import {captcha_token} from './information.js';

//Eventually needs to be updated to grab nested iframe 
// having issues with getting the iframe element title 
// rather than the title of the iframe (e.g. a nestd <title> element)
async function getNestedFrame(frame, indent, title) {
    try{
        // console.log(indent + await frame.title());
        const frameElement = await frame.frameElement();
        const frameTitle = await frameElement.evaluate(el => el.getAttribute('title'));
        console.log(indent + frameTitle);
        if (frameTitle == title) {
            return frame;
        }
        
        for (const child of frame.childFrames()) {
            return await getNestedFrame(child, indent + '  ', title);
        }
    }
    catch (error) {
        console.log('error getting child frames',error);
    }
  };

async function getTokenFrame(page) {
    console.log("Looking for FunCaptcha iframe")
    const iframeSelector = 'iframe[id="captcha-internal"]';
    const iframeElementHandle = await page.$(iframeSelector);
    const iframe = await iframeElementHandle.contentFrame();
    var myFrame = await getNestedFrame(iframe, '', 'Verification challenge')
    console.log('Found token frame');
    return myFrame;
}

async function extractFromToken(token, key) {
    const regex = new RegExp(`${key}=([^|]*)`);
    const match = token.match(regex);
    console.log('match',match);
    return match ? match[1] : null;
}

//Finds the funCaptcha nested iframe and extracts the info needed to solve the captcha
async function get_pk_and_surl(page) {
    console.log("Getting captcha pk and surl")
    var tokenFrame = await getTokenFrame(page);

    console.log('Found token frame');

    var token = null;
    try {
        token = await tokenFrame.$eval('input[name="fc-token"]', (el) => {
            return el.value;
        });
    }
    catch (error) {
        console.log('error getting token from token frame',error);
    }
    console.log(token);

    console.log("Parsing element for pk and surl")
    // Helper to extract key-value pairs from the token string

    const pk = await extractFromToken(token, 'pk');
    const surl = await extractFromToken(token, 'surl');

    console.log('pk:', pk);
    console.log('surl:', decodeURIComponent(surl));
    return [pk, surl, tokenFrame];
}

async function solve_captcha(page) {
    let pk = null;
    let surl = null;
    let tokenFrame = null;
    try {
        var pk_surl_frame = await get_pk_and_surl(page)
        pk = pk_surl_frame[0];
        surl = pk_surl_frame[1];
        tokenFrame = pk_surl_frame[2];
    } catch (error) {
        console.log("Error getting token: ", error)
    }
    if (pk == null ) {
        //surl can be null, but is better if had
        console.log("No pk or surl found")
        return
    }
    else {
        const solver = new TwoCaptcha.Solver(captcha_token);
        // Provide surl (service url) and tc-token
        let response = null;
        console.log('page url',page.url());
        solver.funCaptcha({
            pageurl: page.url(),
            publickey: pk, //3117BF26-4762-4F5A-8ED9-A85E69209A46
            surl: surl
        })
        .then((res) => {
            response = res;
            console.log("Solved captcha: ", response)
        })
        .catch((err) => {
            console.log(err);
        })

    
    console.log('response',response);
    // wait for 4 seconds
    await new Promise(resolve => setTimeout(resolve, 4000));

    if (response) {
        await page.locator('div[id="FunCaptcha"] input[id="fc-token"]').fill(response)
    }
    console.log(result);
    }
}

export { get_pk_and_surl, solve_captcha, getTokenFrame};