
        // nodeEval(`(async () => {
        //     await page.evaluate((id, value) => {
        //     const el = document.querySelector('[id*="phoneNumber-nationalNumber"]');
        //     console.log(el);
        //     if (el) {
        //         el.value = value;
        //         el.dispatchEvent(new Event('input', { bubbles: true }));
        //     }
        // }, "phoneNumber-nationalNumber", "999999999999");
        // })();`)
        nodeEval(`(async () => {
            const x = await page.locator('[id*="phoneNumber-nationalNumber"]').click();
            console.log(x);
            await page.keyboard.type('999999999999', { delay: 100 });
            await page.keyboard.press('Enter');
        })();`)
        nodeEval(`
             (async () => { 
                 const x = await page.$$eval('[class*="XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl"]', els => els.map(el => el.textContent));
                 return JSON.stringify(x);
               }
             )();`
        )
            .then(res => console.log(JSON.parse(res)))
            .catch(err => console.error(err));

        ///find linkedin easy apply input boxes
         nodeEval(`
             (async () => { 
                 const x = await page.$$eval('[class*="XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl"] label', els => els.map(el => el.textContent));
                 return JSON.stringify(x);
               }
             )();`
        )
            .then(res => console.log(JSON.parse(res)))
            .catch(err => console.error(err))

        //Get question ids
        nodeEval(`
            (async () => { 
                const x = await page.$$eval('[class*="XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl"] label', els => els.map(el => [el.getAttribute('for'),el.textContent]));
                return JSON.stringify(x);
              }
            )();`
       )
           .then(res => console.log(JSON.parse(res)))
           .catch(err => console.error(err));