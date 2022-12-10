CSE-312 Project: eCommerce (Auction House)

Description: Making a storefront where users can buy and sell goods. The store will also have an option for users to put items up for auction

Group Members (by ubits): xli256, yiyuanwa, huandong, tvho

* When Click ON the "POST" Drop Down Button on our "Shopping Web Page", Please Click "↓"(Arrow Down) key on the KeyBoard to open the Drop Down Menu.
<img width="1440" alt="Screen Shot 2022-12-09 at 16 40 04" src="https://user-images.githubusercontent.com/75594446/206800661-7bcccde0-2470-44e4-96ac-f7d916d4cd61.png">

* When runing "docker-compose up", make sure you are in the "Server" directory!
Thank you!

* "Session" Cookie is only used on the "Place Bid" button. If user delete the "Session" Cookie, then click "Place Bid", Item price will not be updated.
* "auth_token" Cookie is used on rest of the Pages and features. If user delete the "auth_token" Cookie, then click on any buttons or links expect "Place Bid" button, it will redirect them to our "Login" Page.
