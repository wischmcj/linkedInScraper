
import TwoCaptcha from "@2captcha/captcha-solver"
const frames = await page.frames();


//Eventually needs to be updated to grab nested iframe 
// having issues with getting the iframe element title 
// rather than the title of the iframe (e.g. a nestd <title> element)
async function get_frames(page) {
    // await page.evaluate(() => {
    //     debugger;
    //   });
    for (const currentFrame of frames) {
        dumpFrameTree(currentFrame, '');
    }
    await browser.close();
    
    const main = await page.mainFrame();
    console.log('main',main)

    async function dumpFrameTree(frame, indent) {
        try{
            // const title = await frame.title();
            const title = await page.locator('iframe')
            console.log(indent + title );
        }
        catch (error) {
            console.log('error getting title',error);
        }
        try{    
            const childFrames = await frame.childFrames();
            for (const child of childFrames) {
                await new Promise(resolve => setTimeout(resolve, 5000));
                dumpFrameTree(child, indent + '  ');
            }
        }
        catch (error) {
            console.log('error getting child frames',error);
        }
    }
}

// a worse version of the above.
// Demonstrated how to get elements within an iframe
async function get_iframe(page, title){
    // await page.evaluate(() => {
    //     debugger;
    //   });
    const frames = page.frames();
    let frame = null;
    for (const currentFrame of frames) {
        console.log('Parent frame', currentFrame)
        const frameElement = await currentFrame.frameElement();
        if (frameElement) {
            const frame_name = await frameElement.evaluate(el => el.getAttribute('name'));
            console.log('Parent name', frame_name)
        }
        recurseFrames(currentFrame, '')
        // const frame_title = await frameElement.evaluate(el => el.getAttribute('title'));
        // if (frame_title === title) {
            // frame = currentFrame;
            // break;
        // }
    }
    if (frame) {
      const text = await frame.$eval('.selector', element => element.textContent);
      console.log(text);
    } else {
      console.error('Frame with name "myframe" not found.');
    }
    return frame;
}


//Finds the funCaptcha nested iframe and extracts the info needed to solve the captcha
async function get_pk_and_surl(page) {
    
    console.log("Looking for FunCaptcha")
    
    // const iframeSelector = 'iframe[id="arkoseframe"]'; //title = "Fun Captcha Challenge"
    // const iframeElementHandle = await page.$(iframeSelector);
    // await new Promise(resolve => setTimeout(resolve, 5000));
    // const iframeProper = iframeElementHandle.contentFrame();
    // console.log('set proper')
    // const elementsInIframe = await iframeProper.$$eval('div', (elements) => {
    //     return elements.map((element) => element.textContent);
    //   });
    // console.log(elementsInIframe)


    // const iframeHandle = await page.$(iframeSelector);

    const innerIframeHandle = await page.$('iframe[title="Verification challenge"]');
    await innerIframeHandle.waitForSelector('input[name="fc-token"]')
    
    const iframe = iframeElementHandle.contentFrame();
    const token = await page.evaluate(() => {
        return document.querySelector('input[name="fc-token"]').value;
    });
    console.log(token)

    console.log("Parsing element for pk and surl")
    // Helper to extract key-value pairs from the token string
    function extractFromToken(token, key) {
        const regex = new RegExp(`${key}=([^|]*)`);
        const match = token.match(regex);
        return match ? match[1] : null;
    }

    const pk = extractFromToken(fcTokenValue, 'pk');
    const surl = extractFromToken(fcTokenValue, 'surl');

    console.log('pk:', pk);
    console.log('surl:', decodeURIComponent(surl));
    return [pk, surl];
}

async function solve_captcha(page) {
    let pk = null;
    let surl = null;
    try {
        [pk, surl] = await get_pk_and_surl(page)
    } catch (error) {
        console.log("Error: ", error)
        const pk = await page.locator('div[id="FunCaptcha"] input[id="FunCaptcha-Token"]').getAttribute('value')
        console.log("Token: ", pk)
    }
    if (pk == null ) {
        //surl can be null, but is better if had
            console.log("No pk or surl found")
            return
    }
    else {
        const solver = new TwoCaptcha.Solver();
        // Provide surl (service url) and tc-token
        let response = null;
        solver.funCaptcha({
            pageurl: "https://www.linkedin.com/checkpoint/challenge/AgHdODDXPeZ7XQAAAZfRuPh-oPc5yGs94Md7vRAeJfX795wJGa2OwZGrlxDPf4ZTT5kosFVQb3HmgbjhE5Y9SOCm2DOKOw?ut=1N9fdcA7-5sHQ1",
            publickey: token,
            surl: surl
        })
        .then((res) => {
            response = res;
            console.log("Solved captcha: ", response)
        })
        .catch((err) => {
            console.log(err);
        })

    // wait for 4 seconds
    await new Promise(resolve => setTimeout(resolve, 4000));

    if (response) {
        await page.locator('div[id="FunCaptcha"] input[id="fc-token"]').fill(response)
    }
    console.log(result);
}

export { get_pk_and_surl, solve_captcha };