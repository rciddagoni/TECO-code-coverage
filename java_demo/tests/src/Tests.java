import Pages.AboutPage;
import Pages.AppPage;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.After;
import org.junit.BeforeClass;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import static org.junit.Assert.assertEquals;

public class Tests {

    private static WebDriver _Webdriver;


    @BeforeClass
    public static void Setup() {
        _Webdriver = new ChromeDriver();

    }

    @AfterClass
    public static void Teardown() {
        _Webdriver.close();
    }

    @After
    public void TestTeardown() {
        try
        {
            //ugly but we are instrumenting here, need to make sure the rest api call to instrumenting server
            //happens before test finishes forever, we need its stats
            Thread.sleep(3000);
        }
        catch (InterruptedException e)
        {
            System.out.println(e.toString());
        }

    }




    @Test
    public void test1() {
        TecoServiceHelper.SetTest("T1","Verify expected output is displayed when button 1 is clicked","main.js");
        AppPage app = new AppPage(_Webdriver);
        app.ClickButton(1);
        String outputText = app.GetOutputText();
        assertEquals("Output invalid!", "function 3 output", outputText);

    }

    @Test
    public void test2() {
        TecoServiceHelper.SetTest("T2","test that code attached to button2 is triggered when the button is clicked","main.js");
        AppPage app = new AppPage(_Webdriver);
        app.ClickButton(2);
        String outputText = app.GetOutputText();
        assertEquals("Output invalid!", "function 2 output", outputText);

    }


    @Test
    public void test3() {
        TecoServiceHelper.SetTest("T3","Verify about page is displayed when about link is clicked","navigation");
        AppPage app = new AppPage(_Webdriver);
        AboutPage aboutPage=app.NavigateToAboutPage();
        assertEquals("About page was not visited!", "http://localhost:8787/about.html", _Webdriver.getCurrentUrl());

    }
}

