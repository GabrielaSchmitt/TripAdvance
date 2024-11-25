# start_date(DD/MM/YYYY),start_city,end_city_airline,duration(minutes),price(dol)
import os

PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch
import asyncio
from pyppeteer_stealth import stealth

baseUrl = "https://www.maxmilhas.com.br/passagens-aereas/"
flights = [
    "sao-paulo-br/salvador-br",
    "sao-paulo-br/curitiba-br",
    "sao-paulo-br/rio-de-janeiro-br",
    "sao-paulo-br/fortaleza-br",
    "sao-paulo-br/recife-br",
    "sao-paulo-br/porto-alegre-br",
    "sao-paulo-br/brasilia-br",
    "sao-paulo-br/belo-horizonte-br",
    "sao-paulo-br/natal-br",
    "sao-paulo-br/florianopolis-br",
    "curitiba-br/rio-de-janeiro-br",
    "curitiba-br/salvador-br",
    "curitiba-br/fortaleza-br",
    "curitiba-br/recife-br",
    "curitiba-br/porto-alegre-br",
    "curitiba-br/brasilia-br",
    "curitiba-br/belo-horizonte-br",
    "curitiba-br/natal-br",
    "curitiba-br/florianopolis-br",
    "rio-de-janeiro-br/salvador-br",
    "rio-de-janeiro-br/fortaleza-br",
    "rio-de-janeiro-br/recife-br",
    "rio-de-janeiro-br/porto-alegre-br",
    "rio-de-janeiro-br/brasilia-br",
    'rio-de-janeiro-br/belo-horizonte-br',
    'rio-de-janeiro-br/natal-br',
    'rio-de-janeiro-br/florianopolis-br',
    'salvador-br/fortaleza-br',
    'salvador-br/recife-br',
    'salvador-br/porto-alegre-br',
    'salvador-br/brasilia-br',
    'salvador-br/belo-horizonte-br',
    'salvador-br/natal-br',
    'salvador-br/florianopolis-br',
    'fortaleza-br/recife-br',
    'fortaleza-br/porto-alegre-br',
    'fortaleza-br/brasilia-br',
    'fortaleza-br/belo-horizonte-br',
    'fortaleza-br/natal-br',
    'fortaleza-br/florianopolis-br',
    'recife-br/porto-alegre-br',
    'recife-br/brasilia-br',
    'recife-br/belo-horizonte-br',
    'recife-br/natal-br',
    'recife-br/florianopolis-br',
    'porto-alegre-br/brasilia-br',
    'porto-alegre-br/belo-horizonte-br',
    'porto-alegre-br/natal-br',
    'porto-alegre-br/florianopolis-br',
    'brasilia-br/belo-horizonte-br',
    'brasilia-br/natal-br',
    'brasilia-br/florianopolis-br',
    'belo-horizonte-br/natal-br',
    'belo-horizonte-br/florianopolis-br',
    'natal-br/florianopolis-br'
]

async def main():
    csv = open("flights.csv", "w")
    csv.write("start_date,start_city,end_city_airline,duration(minutes),price(dol)\n")
    browser = await launch(headless=False)
    page = await browser.newPage()
    await stealth(page)
    for flight in flights:
        url = f"{baseUrl}{flight}"
        print(url)
        await page.goto(url)
        try:
            melhoresOfertasFound = False
            travelLegFound = False
            try:
                await page.waitForSelector('.melhores-ofertas', timeout=10000)
                melhoresOfertasFound = True
            except Exception as e:
                print('Melhores ofertas not found')
            try:
                await page.waitForSelector('.travel-leg', timeout=10000)
                travelLegFound = True
            except Exception as e:
                print('Travel leg not found')

            if not melhoresOfertasFound:
                continue

            flightsFound = await page.querySelectorAll('.card-infogreen')
            travelLegs = await page.querySelectorAll('.travel-leg')
            if not flightsFound:
                continue
            counterFlights = 0
            print(f'Flights found: {len(flightsFound)}')
            while len(flightsFound) > 0 and counterFlights < len(flightsFound) and counterFlights < 4:
                print(f'Flight: {counterFlights}')
                flightsFound = await page.querySelectorAll('.card-infogreen')
                flightFound = flightsFound[counterFlights]
                src = await flightFound.getProperty('href')
                srcText = await src.jsonValue()
                srcText = srcText.replace("RT", "OW")
                info = await flightFound.querySelector('.card-infogreen--info')
                infoText = await info.getProperty('textContent')
                infoText = (await infoText.jsonValue()).strip()
                infoText = infoText.split(' ')
                date = infoText[2].strip()
                start_city = flight.split("/")[0].split("-br")
                end_city = flight.split("/")[1].split("-br")
                start_city = start_city[0].replace("-", " ").capitalize()
                end_city = end_city[0].replace("-", " ").capitalize()
                await page.goto(srcText)
                await page.evaluate('''() => { window.scrollBy(0, window.innerHeight); }''')    
                try:
                    await page.waitForSelector('.text-cia', timeout=60000)
                except Exception as e:
                    print('Airline not found')
                    await page.goBack()
                    await asyncio.sleep(3)
                    counterFlights += 1
                    continue
                airline = await page.querySelector('.text-cia')
                if not airline:
                    print('Airline not found')
                    await page.goBack()
                    await asyncio.sleep(3)
                    counterFlights += 1
                    continue
                airlineText = await airline.getProperty('textContent')
                airlineText = await airlineText.jsonValue()
                time = await page.querySelector('.time')
                if not time:
                    print('Time not found')
                    await page.goBack()
                    await asyncio.sleep(3)
                    counterFlights += 1
                    continue
                timeText = await time.getProperty('textContent')
                timeText = await timeText.jsonValue()
                duration = convert_date(timeText)
                price = await page.querySelector('.content-price')
                if not price:
                    print('Price not found')
                    await page.goBack()
                    await asyncio.sleep(3)
                    counterFlights += 1
                    continue
                lineThroughFound = False
                priceFound = False
                try:
                    await page.waitForSelector('.line-through', timeout=60000)
                    lineThroughFound = True
                except Exception as e:
                    print('Line Through not found')
                if not lineThroughFound:
                    try:
                        await page.waitForSelector('.content-price>div>p>span', timeout=5000)
                        priceFound = True
                    except Exception as e:
                        print('Price not found')                        
                if not lineThroughFound and not priceFound:
                    await page.goBack(timeout=60000)
                    await asyncio.sleep(3)
                    counterFlights += 1
                    continue
                if lineThroughFound:
                    priceAirline = await page.querySelector('.line-through')
                    if not priceAirline:
                        print('Price airline not found')
                        await page.goBack()
                        await asyncio.sleep(3)
                        counterFlights += 1
                        continue
                    priceAirline = await priceAirline.getProperty('textContent')
                    if not priceAirline:
                        print('Price airline text not found')
                        await page.goBack()
                        await asyncio.sleep(3)
                        counterFlights += 1
                        continue
                    priceAirline = await priceAirline.jsonValue()
                    priceAirline = priceAirline.replace("R$", "").replace(",", ".").strip()
                else:
                    priceAirline = await price.querySelector('.content-price>div>p>span')
                    if not priceAirline:
                        print('Price airline not found')
                        await page.goBack()
                        await asyncio.sleep(3)
                        counterFlights += 1
                        continue
                    priceAirline = await priceAirline.getProperty('textContent')
                    if not priceAirline:
                        print('Price airline text not found')
                        await page.goBack()
                        await asyncio.sleep(3)
                        counterFlights += 1
                        continue
                    priceAirline = await priceAirline.jsonValue()
                    priceAirline = priceAirline.replace("R$", "").replace(",", ".").strip()
                print(date, start_city, end_city, airlineText, duration, priceAirline)
                csv.write(f'{date},{start_city},{end_city},{airlineText},{duration},{priceAirline}\n')
                await asyncio.sleep(3)
                await page.goBack()
                counterFlights += 1
            counterTravelLegs = 0
            print(f'Travel Legs found: {len(travelLegs)}')
            if travelLegFound and travelLegs:
                while len(travelLegs) > 0 and counterTravelLegs < len(travelLegs) and counterTravelLegs < 4:
                    print(f'Travel Leg: {counterTravelLegs}')
                    travelLegs = await page.querySelectorAll('.travel-leg')
                    travelLeg = travelLegs[counterTravelLegs]
                    aElement = await travelLeg.querySelector('a')
                    src = await aElement.getProperty('href')
                    srcText = await src.jsonValue()
                    srcText = srcText.replace("RT", "OW")
                    cities = await travelLeg.querySelectorAll('.travel-leg__city')
                    start_city = await page.evaluate('(element) => element.childNodes[0].textContent', cities[0])
                    end_city = await page.evaluate('(element) => element.childNodes[0].textContent', cities[1])
                    await page.goto(srcText)
                    await page.evaluate('''() => { window.scrollBy(0, window.innerHeight); }''')
                    try:
                        await page.waitForSelector('.text-cia', timeout=60000)
                    except Exception as e:
                        print('Airline not found')
                        await page.goBack(timeout=60000)
                        await asyncio.sleep(3)
                        counterTravelLegs += 1
                        continue
                    airline = await page.querySelector('.text-cia')
                    if not airline:
                        print('Airline not found')
                        await page.goBack(timeout=60000)
                        await asyncio.sleep(3)
                        counterTravelLegs += 1
                        continue
                    airlineText = await airline.getProperty('textContent')
                    airlineText = await airlineText.jsonValue()
                    time = await page.querySelector('.time')
                    if not time:
                        print('Time not found')
                        await page.goBack(timeout=60000)
                        await asyncio.sleep(3)
                        counterTravelLegs += 1
                        continue
                    timeText = await time.getProperty('textContent')
                    timeText = await timeText.jsonValue()
                    duration = convert_date(timeText)
                    price = await page.querySelector('.content-price')
                    if not price:
                        print('Price not found')
                        await page.goBack(timeout=60000)
                        await asyncio.sleep(3)
                        counterTravelLegs += 1
                        continue
                    lineThroughFound = False
                    priceFound = False
                    try:
                        await page.waitForSelector('.line-through', timeout=5000)
                        lineThroughFound = True
                    except Exception as e:
                        print('Line Through not found')

                    if not lineThroughFound:
                        try:
                            await page.waitForSelector('.content-price>div>p>span', timeout=5000)
                            priceFound = True
                        except Exception as e:
                            print('Price not found')
                    if not lineThroughFound and not priceFound:
                        await page.goBack(timeout=60000)
                        await asyncio.sleep(3)
                        counterTravelLegs += 1
                        continue
                    header = await page.querySelector('.header-stretch')
                    date = await header.querySelector('span')
                    date = await date.getProperty('textContent')
                    date = await date.jsonValue()
                    date = date.split(" ")[3]
                    if lineThroughFound:
                        priceAirline = await price.querySelector('.line-through')
                        if not priceAirline:
                            print('Price airline not found')
                            await page.goBack(timeout=60000)
                            counterTravelLegs += 1
                            continue
                        priceAirline = await priceAirline.getProperty('textContent')
                        priceAirline = await priceAirline.jsonValue()
                        priceAirline = priceAirline.replace("R$", "").replace(",", ".").strip()
                    else:
                        priceAirline = await price.querySelector('.content-price>div>p>span')
                        if not priceAirline:
                            print('Price airline not found')
                            await page.goBack(timeout=60000)
                            counterTravelLegs += 1
                            continue
                        priceAirline = await priceAirline.getProperty('textContent')
                        priceAirline = await priceAirline.jsonValue()
                        priceAirline = priceAirline.replace("R$", "").replace(",", ".").strip()
                    print(date, start_city, end_city, airlineText, duration, priceAirline)
                    csv.write(f'{date},{start_city},{end_city},{airlineText},{duration},{priceAirline}\n')
                    await asyncio.sleep(3)
                    await page.goBack(timeout=60000)
                    counterTravelLegs += 1
        except Exception as e:
            print(e)
            print("Falha ao buscar voos para a rota: " + flight)
            continue
            
    csv.close()
    await browser.close()

def convert_date(time):
    time = time.split(" ")
    minutes = 0
    for t in time:
        if "h" in t:
            minutes += int(t.replace("h", "")) * 60
        if "m" in t:
            minutes += int(t.replace("m", ""))
    return minutes
        
asyncio.get_event_loop().run_until_complete(main())