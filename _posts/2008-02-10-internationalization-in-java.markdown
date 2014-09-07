---
layout: post
status: publish
published: true
title: Internationalization in Java
excerpt: "This is a quick tutorial on how to make it easy to support multiple languages
  in your Java programs.\r\n\r\n"
wordpress_id: 9
wordpress_url: http://www.thedreaming.org/2008/02/10/internationalization-in-java/
date: '2008-02-10 17:19:56 -0500'
date_gmt: '2008-02-10 22:19:56 -0500'
categories:
- Software
- Java
tags:
- Java
- Internationalization
- i18n
- tutorial
comments: []
---
<p>This is a quick tutorial on how to make it easy to support multiple languages in your Java programs.</p>
<p><a id="more"></a><a id="more-9"></a></p>
<div class= "sidebar">
<h1>What is i18n?</h1>
<p>You will often see references to "i18n" when reading about internationalization.  This isn't some strange standard or protocol, it actually just stands for "internationalization".  The joke is that the word "internationalization" is far too long to type, and therefore it is abbreviated to "i18n", since "internationalization" is an "i" followed by 18 letters and an "n".  Similarly, "l10n" stands for "Localization".
</p></div>
<p>Internationalization in Java is accomplished through the use of the <a target="_blank" href="http://java.sun.com/javase/6/docs/api/java/util/ResourceBundle.html">ResourceBundle</a> object, and most often specifically the <a target="_blank" href="http://java.sun.com/javase/6/docs/api/java/util/PropertyResourceBundle.html">PropertyResourceBundle</a>.</p>
<h2>A Quick Example</h2>
<p>Let's start with the classic of computer science examples:</p>
<div class="code">
<pre>static public void main(String args[]) {
  System.out.println("Hello World!");
}
</pre>
</div>
<p>The problem here, as you likely know since you're reading this tutorial, is that we've just hard-coded the string "Hello World" into our code, and when we export our program to another country where they don't speak English, we'll have a hard time changing our program.</p>
<p>Instead, we create a "properties" file.  Typically this properties file would go inside the jar file, in a subdirectory called "resources".</p>
<div class="file">
<div class="filename">/resources/MyApplicationStrings.properties</div>
<div class="filecontent">
    # Strings for our program<br />
    helloMessage=Hello World!
  </div>
</div>
<p>The properties file lists a series of keys, and associates them with messages.  In this case, we have a single key "helloMessage", associated with the message "Hello World!".</p>
<p>Then in our code:</p>
<div class="code">
<pre>static public void main(String args[]) {
  Locale locale = new Locale("en");
  ResourceBundle messages = ResourceBundle.getBundle(
    "resources/MyApplicationStrings", locale);
  String helloMessage = messages.getString("helloMessage");
  System.out.println(helloMessage);
}
</pre>
</div>
<p>So, what have we done here?  First, we create a Locale object:</p>
<div class="code">
<pre>  Locale locale = new Locale("en");
</pre>
</div>
<p>A Locale represents information first about the language we display information in (in this case "en" for "English"), and second it can represent information about the country to display the information in.  The reason for specifying a language is obvious; we want our program to be displayed in different languages.  We also specify a country so that we can make the messages we display specific to the location; the formats of dates and numbers might be different in different countries.  Even a language might be different from country to country; for example British and Canadian English have some spelling differences from US English.  To specify a Locale of English in the United States, for example, you would use:</p>
<div class="code">
<pre>  Locale locale = new Locale("en", "US");
</pre>
</div>
<p>We then get the resource bundle specific to the locale we're using.  Since we only have one properties file, that's the properties file we'll get.  We'll see more about how to create property files in other languages in a moment.</p>
<div class="code">
<pre>  ResourceBundle messages = ResourceBundle.getBundle(
    "resources/MyApplicationStrings", locale);
</pre>
</div>
<p>Note that we don't pass "resources/MyApplicationStrings.properties" to the getBundle() method.  We leave off the ".properties" because we are not passing a single properties file, but the name of the bundle.  As we'll see, a bundle may consist of many properties files.</p>
<p>Finally, we get the string which corresponds to the key "helloMessage" out of the resource bundle.</p>
<div class="code">
<pre>  String helloMessage = messages.getString("helloMessage");
</pre>
</div>
<h2>Creating .properties Files for Different Languages</h2>
<p>Let's create another properties file:</p>
<div class="file">
<div class="filename">/resources/MyApplicationStrings_fr.properties</div>
<div class="filecontent">
    # French properties file.<br />
    helloMessage=Bonjour Monde!
  </div>
</div>
<p>Note that this properties file's name ends in "_fr".  We now have a two different properties files: a "base" properties file and the French language properties file, both of which are in the "resources/MyApplicationStrings" bundle.  We then modify our Java program to use a French locale.  Since both properties files are part of the same bundle, the call to getBundle() doesn't change.  Only the locale changes:</p>
<div class="code">
<pre>static public void main(String args[]) {
  Locale locale = new Locale(<span class="changes">"fr"</span>);
  ResourceBundle messages = ResourceBundle.getBundle(
    "resources/MyApplicationStrings", locale);
  String helloMessage = messages.getString("helloMessage");
  System.out.println(helloMessage);
}
</pre>
</div>
<p>Now our program outputs a message in French.  </p>
<p>If we specify a locale with a language that doesn't exist, Java will fall back on the base properties file.  Note that even if the properties file for a specific language does exist, if a message does not exist in the language specific properties file, then Java will try to find the message in the base properties file.  So, for example, if someone adds a new "goodbye=Goodbye!" to the base properties file, but forgets to add it to the French language file, and then tries to use the "goodbye" key in the program with a French local, "Goodbye!" will still be displayed.</p>
<h2>Creating .properties Files for Different Countries</h2>
<p>Let's create two more properties files:</p>
<div class="file">
<div class="filename">/resources/MyApplicationStrings_en_US.properties</div>
<div class="filecontent">
    # US English properties file.<br />
    helloMessage=Hello World!
  </div>
</div>
<div class="file">
<div class="filename">/resources/MyApplicationStrings_en_CA.properties</div>
<div class="filecontent">
    # Canadian English properties file.<br />
    helloMessage=Hello World, eh?
  </div>
</div>
<p>Note that these filenames have not only a language code ("en" for English), but also a country code ("US" for the United States, and "CA" for Canada).  Again, these files are still part of the same bundle.  Now, if we set our locale to "English, "Canadian":</p>
<div class="code">
<pre>  Locale locale = new Locale("en", "CA");
</pre>
</div>
<p>we will see a different message than for "English", "United States".</p>
<p>The order in which ResourceBundle's "getBundle()" method looks for property files is somewhat complicated, but if you're interested, have a look at the <a target="_blank" href="http://java.sun.com/javase/6/docs/api/java/util/ResourceBundle.html#getBundle(java.lang.String,%20java.util.Locale,%20java.lang.ClassLoader,%20java.util.ResourceBundle.Control)">JavaDoc for the getBundle()</a> method.  Essentially, though, getBundle() will first look for a file that matches both the language and the locale.  If one cannot be found, it will instead try to find one which matches the language (even if it is in a different locale).  Failing that it will look for one which matches the locale (even if it is in a different language).  Finally, failing to find country or locale, it will resort to the base bundle.</p>
<h2>Messages with Arguments</h2>
<p>Not all the messages we display consist of pre-defined static Strings.  For example, after a user logs in, we might want to welcome them.</p>
<div class="code">
<pre>  System.out.println("Hello " + username + "! Welcome to " + programName + "!");
</pre>
</div>
<p>You might be tempted to make the "Hello" and "Welcome to" parts of this string into two different entries in the properties file, but there's a better way.  In our properties file, we add a new line:</p>
<div class="file">
<div class="filename">/resources/MyApplicationStrings.properties</div>
<div class="filecontent">
    # Strings for our program<br />
    helloMessage=Hello World!<br />
    welcome=Hello {0}!  Welcome to {1}!
  </div>
</div>
<p>The line in the properties file contains special markers which indicate where our arguments should go.  The {0} refers to the 0th argument in the argument array.  Then, in our code, we construct an array of arguments we want to put into the message, and use a MessageFormat object to do the replacement:</p>
<div class="code">
<pre>public static void main(String[] args) {
  Locale locale = new Locale("en", "US");
  String username = "Jason";
  String programName = "The I18n Tutorial";

  ResourceBundle messages = ResourceBundle.getBundle(
    "resources/MyApplicationStrings", locale, ClassLoader.getSystemClassLoader());
  String welcomeMessage = messages.getString("welcome");
  Object [] messageArguments = new Object [] {username, programName};
  MessageFormat formatter = new MessageFormat(welcomeMessage, locale);
  String output = formatter.format(messageArguments);
  System.out.println(output);
}
</pre>
</div>
<p>Note that we pass the locale to the MessageFormat constructor.  In this particular example, the MessageFormat doesn't care about locale, but by setting the locale, we can get MessageFormat to format dates and numbers in a location specific way.  The correct symbol will be chose for currencies, for example.</p>
<p>The format for the markers in the properties file is different for dates and numbers.  Here are a few examples:</p>
<div class="file">
<div class="filename">/resources/DatesAndNumbers.properties</div>
<div class="filecontent">
    # Display the current date and time.  The first argument in the arguments<br />
    # array should be an instance of java.util.Date. Note that we're using one<br />
    # Date object for both the date and time parts of the message.  This<br />
    # might display something like:<br />
    #<br />
    #   The time is now 1:43 PM and the date is February 10, 2008.<br />
    #<br />
    # but remember this might change, depending on the locale.</p>
<p>    dateAndTime = The time is now {0,time,short} and the date is {0,date,long}.</p>
<p>    # Display a currency in a location specific way.  The first argument<br />
    # in the arguments array should be an instance of Number,  such<br />
    # as java.lang.Float.  This might display something like "Balance: $20.45".</p>
<p>    balance = Balance: {0,number,currency}.
  </p></div>
</div>
<p>For more information, see the <a target="_blank" href="http://java.sun.com/javase/6/docs/api/java/text/MessageFormat.html">JavaDoc for MessageFormat</a>.</p>
<h2>Further Reading</h2>
<p>Sun has an excellent <a target="_blank" href="http://java.sun.com/docs/books/tutorial/i18n/index.html">trail about internationalization</a> on their web site, which goes into greater detail than this tutorial.</p>
