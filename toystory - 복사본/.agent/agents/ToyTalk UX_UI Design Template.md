# **ToyTalk UX/UI Design Template**

This template provides a structured blueprint for designing the user experience (UX) and user interface (UI) of **ToyTalk**, an AI‑powered conversation platform for children. Use it to guide wireframes, mockups, and production assets in tools like Figma or Notion.

## **Overview**

ToyTalk lets children aged **4–7** converse with their favourite toys. A parent registers a toy by taking a picture; the system transforms it into a colourful cartoon avatar and assigns an appropriate voice profile. Children speak to the character using the microphone, and the character responds in real time via a multimodal AI service. Parents can review conversations later in a slide‑style viewer.

The design must feel playful and magical for kids, yet reassuring and controllable for parents. It should be **fast**, **safe**, and **accessible**, with clear flows and engaging micro‑interactions.

## **Design Goals**

* **Child‑friendly**: Colours, typography and iconography should be soft and inviting. Tap targets must be large enough for small fingers. Language should be simple and encouraging.

* **Safe**: The UI must incorporate safety features (e.g. age gating, content filters, parent locks) and never expose system prompts. Conversation logs are visible only to authenticated parents.

* **Fast and responsive**: Character creation and chat responses should provide immediate feedback via animations and progress indicators. Follow the latency budgets defined in the technical specification (e.g. \< 5 s for character generation).

* **Consistent across platforms**: Design for Android and iOS using Flutter’s theming. Use responsive layouts that adapt to different screen sizes and orientations.

* **Accessible**: Ensure contrast ratios meet WCAG AA guidelines. Support screen readers and voice input. Provide fallbacks (e.g. text transcripts) for audio elements.

## **Personas**

### **Child**

* Age: 4–7 years old.

* Goals: Play with their toy character, tell stories, ask questions, and receive friendly responses.

* Needs: Simple navigation, large buttons, colourful visuals, immediate feedback (animations and sounds).

* Pain points: Small hands and limited reading ability; easily frustrated by delays or errors.

### **Parent**

* Age: 25–45 years old.

* Goals: Register toys, manage the child’s account, monitor conversation history, ensure safety and privacy.

* Needs: Clear controls for adding/removing toys, easy access to logs and summaries, assurance that the system filters inappropriate content.

* Pain points: Complex onboarding, unclear error messages, lack of transparency.

## **Key User Flows**

Use these high‑level flows when sketching wireframes and interactions. Each step should include happy paths and fallback states (loading, empty, error, offline). Numbered lists here correspond to primary actions.

### **1\. Onboarding & Authentication**

1. Launch the app and choose **Parent** or **Child** mode. If the user is a parent, prompt for email/Google authentication; if a child, create an anonymous session linked to the parent’s UID.

2. Request camera and microphone permissions with friendly copy explaining why they are needed.

3. For parents, display an introduction about safety features and how to use the app. For children, transition directly to the **My Toys** screen.

### **2\. My Toys (Library)**

1. Display a grid of **Toy Cards** showing the avatar thumbnail and toy name. The grid should use a **2‑column** layout in portrait and **3‑column** layout in landscape/tablet.

2. Provide a prominent **“+ Add Toy”** button. If there are no toys yet, show an empty state with a friendly illustration and a call‑to‑action.

3. Tapping a card opens the **Talk** screen (child) or a **Details** panel (parent) where the parent can rename or delete the toy.

4. Long‑press or swipe a card to reveal management actions (rename/delete) in parent mode. These actions should be hidden in child mode.

### **3\. Create Toy (Character Creation)**

1. Open the camera with clear instructions like “Take a picture of your toy.” Provide an option to pick from the gallery. Use large shutter and cancel buttons.

2. After capturing, show a **preview** with retake and continue controls. Let the parent or child enter a name; validate required fields.

3. When the user confirms, display a **magical transformation animation**: show sparkles and a dissolving transition while the backend generates the avatar. Include a progress indicator (“Making magic…”) and a skip or cancel option for long operations.

4. Once complete, present the new avatar with a bounce animation and play a greeting such as “Hi\! I’m \[toy name\]\!” Show a button to **Save & Go to My Toys**.

### **4\. Talk (Voice Chat)**

1. Show the character avatar at the top, with a text bubble area beneath for the chat history. The child’s messages and the character’s responses should have distinct colours and bubble shapes.

2. Include a **large microphone button** at the bottom centre. When pressed, record audio and animate a waveform or pulsating ring. Support barge‑in: if the child speaks while the character is talking, the current audio stops and recording begins.

3. Stream audio to the backend and display interim text transcripts. Use skeleton loaders for messages waiting on the AI response.

4. Play the response audio, show the transcript in a bubble, and auto‑scroll to the latest message. Provide a button to end the session, which updates the **sessions** table.

5. Handle errors gracefully: show a friendly message (“Hmm… I didn’t catch that. Can you try again?”) and provide a retry button. If the network drops, indicate reconnection attempts and fallback to turn‑based chat.

### **5\. Parent Dashboard & Logs**

1. In parent mode, present a list of sessions grouped by date (e.g. “2026‑02‑28”). Each list item shows the toy avatar, number of messages, and session duration.

2. Selecting a date opens a **Slide Viewer** (PageView) that displays individual messages in chronological order. Use swipe gestures to navigate and show time stamps.

3. Offer filters (toy name, date range) and a search bar. Provide buttons to access weekly summaries and export options if required.

4. Clearly label sensitive data and ensure it is only visible to authenticated parents. Provide navigation back to **My Toys**.

## **Screen Templates & Components**

### **Onboarding Screen**

| Element | Purpose |
| ----- | ----- |
| **App logo & tagline** | Introduce ToyTalk and set a playful tone. |
| **Mode selection cards** | Large cards or buttons for “I’m a Parent” and “I’m a Child.” Use simple icons. |
| **Permission prompts** | Explain why the app needs camera/microphone access. Present buttons to allow or deny. |
| **Progress indicators** | Show loading animations during authentication. |

### **Toy Card Component**

* Contains an avatar image in a circular or rounded‑square frame.

* Shows the toy name below the image using a friendly font.

* Optionally displays a badge (e.g. unread conversations) for parent mode.

* Supports tap (open talk or details) and long press (manage) interactions.

### **Conversation Bubbles**

* Use contrasting colours for child and character messages (e.g. child: light blue; character: pastel yellow).

* Keep text large and limited to one or two short sentences as specified in **C3** of the technical spec.

* Attach time stamps subtly under parent logs; omit them on the child chat screen to reduce clutter.

### **Slide Viewer**

* Implement using Flutter’s **PageView** to allow swipe left/right navigation.

* Each slide represents a single message (role \+ text) with large typography.

* Include a bottom progress bar or dot indicators to show the number of messages in the session.

### **Action Buttons**

* **Primary Button**: Filled background with high contrast; used for main actions such as “Add Toy,” “Save,” or “Record.” Minimum height 48 px.

* **Secondary Button**: Outline style; used for less critical actions like “Cancel” or “Retake.”

* **Icon Buttons**: Used for navigation (back), microphone, camera, or deleting items. Ensure a minimum touch area of 48 × 48 px.

## **Colour & Typography Guide**

Use a small palette of soft, high‑contrast colours. The values below are suggestions; adjust them to meet the brand mood.

| Name | Hex/Description |
| ----- | ----- |
| **Primary** | `#4DA9E0` – a friendly sky blue used for primary buttons and links |
| **Secondary** | `#F9C74F` – a warm yellow for highlights and accents |
| **Accent** | `#F9844A` – a playful coral for active states and animations |
| **Background** | `#FFFFFF` or very light cream for maximum contrast |
| **Surface** | `#F5F5F5` – light grey for cards and input fields |
| **Error** | `#E76F51` – soft red for error messages and alerts |

For typography, choose a sans‑serif typeface that is round and readable. Flutter’s default **Roboto** or **Nunito** are suitable choices. Use the following hierarchy:

* **Display/Text Large**: 32 – 40 pt for headings and names.

* **Body**: 16 – 18 pt for conversational text.

* **Caption**: 12 – 14 pt for hints and timestamps.

Ensure line spacing and letter spacing create enough breathing room for children learning to read. Support dynamic type scaling via Flutter’s `MediaQuery.textScaleFactor` to accommodate accessibility settings.

## **Accessibility & Safety**

* **Contrast & readability**: All text and interactive elements must meet at least a 4.5:1 contrast ratio. Avoid placing text over busy backgrounds.

* **Touch targets**: Provide a minimum touch area of 48 × 48 pixels. Space controls to prevent accidental taps.

* **Voice & vibration feedback**: Play subtle sounds or haptic feedback on button presses to assure the child that the app is responding.

* **Screen reader support**: Set meaningful `semanticsLabel` properties on widgets. Include hidden labels for icons (e.g. “Record audio”).

* **Safety messaging**: When the system cannot answer due to content restrictions, display and voice a friendly alternative (“I’m not sure about that. Would you like to hear a story?”). Always filter sensitive phrases before they reach the child.

* **Parent locks**: Hide toy deletion/renaming behind a confirmation dialog. Optionally implement biometric or passcode locks to prevent children from accessing parent‑only sections.

## **States: Loading, Empty, Error & Offline**

* **Loading**: Use skeleton loaders or shimmer effects rather than spinners to indicate that content (e.g. avatar generation, conversation logs) is on its way. Provide contextual messages (“Creating your character…”).

* **Empty**: When lists have no content, show a cheerful illustration and a brief explanation (“You don’t have any toys yet. Tap \+ to add one\!”).

* **Error**: Display error cards with an icon and one‑line description (“We couldn’t reach the server. Please try again.”). Offer a retry button. Use the error colour sparingly.

* **Offline**: Detect network loss and show a banner (“You’re offline. Reconnecting…”). Cache recent conversations locally and sync them when the connection resumes.

## **Animations & Micro‑Interactions**

Animations bring the experience to life, but they should not distract or confuse children. Use Flutter’s `AnimatedContainer`, `Lottie`, or custom painters to implement:

* **Magic transformation**: A particle or sparkle effect that appears during avatar generation (see §S1.3 of the technical spec). The animation should last 3–5 seconds and mask backend latency.

* **Bounce & scale**: When the avatar appears, scale it up slightly and then settle to draw attention.

* **Waveform**: Show live audio levels while recording to provide feedback that the app is listening.

* **Swipe indicators**: Use gentle motion hints to suggest that parents can swipe through slides.

## **Implementation Notes**

* Use Flutter’s **`ThemeData`** to centralise colours, typography and shapes. Define light and dark themes if required. Apply `Theme.of(context)` throughout widgets.

* Organise the code into **stateless** and **stateful** widgets according to whether they maintain internal state. Use `Provider` or `Riverpod` for application state (e.g. toy list, session status). Avoid keeping heavy logic in the UI layer.

* Fetch data asynchronously with `FutureBuilder` or `StreamBuilder`. Show appropriate loading states while waiting for the API.

* Use **`Navigator`** or a routing package (`go_router`) to manage navigation. Consider deep linking for push notifications or external links.

* Respect the technical constraints from the spec: enforce response length limits (two sentences), handle audio formats correctly, and include safety filters. Integrate JWT authentication for parent features.

---

This template serves as a living document. Update it as the product evolves, incorporating user feedback and insights from usability testing. Always prioritise the needs of children and their caregivers when making design decisions.

