package Pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class AboutPage {
    String _welcomeMessageCss="#welcomeMessage";

    WebElement _welcomeMessage;

    public AboutPage(WebDriver driver)
    {
        //find references
        WebDriverWait wait = new WebDriverWait(driver, 20);
        _welcomeMessage=wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(_welcomeMessageCss)));
    }

    public String GetWelcomeMessage()
    {
        return _welcomeMessage.getText();
    }
}
