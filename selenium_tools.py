from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
cookie='''
Hm_lvt_a1adbfa038f57bb04cf9a0fbd880fad1=1731917500,1733276765,1733404403,1733446289; HMACCOUNT=F29E1EB48ED2CBC1; Hm_lpvt_a1adbfa038f57bb04cf9a0fbd880fad1=1733970085; Hm_lvt_a1adbfa038f57bb04cf9a0fbd880fad1=1730595625,1731917500,1731919554; Hm_lvt_d8bfb560f8d03bbefc9bdecafc4a4bf6=1732095936; BIDUPSID=BF4062ABEE8123E0FCBED3820B6003B2; PSTM=1732932741; H_PS_PSSID=61027_61098_61136_61141_61175_61216_61220_61212_61208_61214_61239_61190_61283_61296; ZFY=WGDYlgCh3m:BbfvIRv:BqDPhLUPG4oFPbclsmISptGcAY:C; BAIDUID=266D769261715E3B3F7A95816296F1C8:FG=1; BAIDUID_BFESS=266D769261715E3B3F7A95816296F1C8:FG=1; __bid_n=19010d2359d057672a270f; BAIDU_WISE_UID=wapp_1733049567831_465; Hm_lvt_186b55f96a17005115e82205e6c004d2=1733220055; RT="z=1&dm=baidu.com&si=fa55b0ba-b738-4d8e-9ac5-747f1f535aea&ss=m4bcbpwu&sl=1&tt=1e5&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=26c&ul=3g4&hd=3g9"; ppfuid=FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGlcv8RcA1xQKfriWJVc7a+LGEimjy3MrXEpSuItnI4KDy6SdkoVDBfnPMf6rio6M072p1N6CkMY1aSnXgB1lGFtQHqkToJfxaYbEh3hm54O4PE5I5MtLWOB8EmCFAOTz6/GgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTIMJmBV3DqpyTuzDwSUDbMyyfzO9u0S9v0HHkJ/i4zKsdnTNS/pLMWceus0e757/UNkQhA4BJH1ZqCtXJJ8GJaKAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIQfQ2f9s1Zza4fKk8UlB3mtI3mRfaKsoLHYD91dEgJUiwwoOjU+/RbFssADRyrekUJdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg5eQg3PzwS3cxyDdVnXm0S3SzlDBMoJre+/eEVILl9qeUssZW5TOkWNIKhuJhXhvX9kqF+JaWVxWe5HhE2e7zcWzinVPKXI+oymb7UrF2I+ZEd6VO50CmaP+JD/V8nCK/kazYq146hp/2XIWCky++QvQau87dgPQPBPOdZfELQaEBSLlhBmNwzEBsxOHy7QZw9iAQNcYCK2xfeYf2imATVV3bwYaC8F4XJ12oqlxKXLxUJaJyL/ORX2lW3xKCro0F9iAQNcYCK2xfeYf2imATVYemNDYxCmdd8ZXU4Cg4htkEQSRUz7L4kkhL4CxkTt2IBjr/vyN58BqfauYSxfP9O4KEVJ4njsvVmNwgrtRSkK2MAD23qY0MlH51PwQdoK9bWx4UhpRCqPktHIslB6EWFA==
'''
def getdriver(url, timeout,withhead:bool):
    """
    得到模拟浏览器
    :return:
    """
    options = webdriver.EdgeOptions()
    options.use_chromium = True

    if not withhead:
        options.add_argument("--headless=new")
        options.add_argument(f'user-agent={user_agent}')

    options.add_argument("--disable-web-security")  # 忽略跨域限制
    driver = webdriver.Edge(options=options)

    try:
        driver.get(url)
    except Exception as e:
        print('无法打开网页')
        print('未知错误：')
        print(e)
        exit(0)
    return driver, WebDriverWait(driver, timeout)