package Pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class AppPage {
    //locators
    String _button1Css="#testButton1";
    String _button2Css="#testButton2";
    String _outputParagraphCss="#output_paragraph";
    String _aboutLinkCss="a";

    //elements
    WebElement _button1;
    WebElement _button2;
    WebElement _outputParagraph;
    WebElement _aboutLink;

    //other
    WebDriver _driverInstance;

    public AppPage(WebDriver driver)
    {
        _driverInstance=driver;
        _driverInstance.get("http://localhost:8787/");

        //find references
        WebDriverWait wait = new WebDriverWait(_driverInstance, 20);
        _button1=wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(_button1Css)));
        _button2=wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(_button2Css)));
        _aboutLink=wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(_aboutLinkCss)));
        _outputParagraph=wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector(_outputParagraphCss)));


    }

    public String GetOutputText()
    {
        return _outputParagraph.getText();
    }

    public void ClickButton(int whichButton)
    {
        switch(whichButton)
        {
            case 1:
            {
                _button1.click();
                break;
            }
            case 2:
            {
                _button2.click();
                break;
            }
        }
    }


    public AboutPage NavigateToAboutPage()
    {
        _aboutLink.click();

        return new AboutPage(this._driverInstance);
    }


}
