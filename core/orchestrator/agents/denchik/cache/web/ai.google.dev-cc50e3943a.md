# Gemini thinking
When you use a thinking model, Gemini reasons internally before responding. The Interactions API surfaces this reasoning via `thought` steps, dedicated steps that appear chronologically alongside function calls, user inputs or model outputs in the `steps` array.

...

| Field | Required | Description |
| `signature` | ✅ Yes | An encrypted representation of the model's internal reasoning state. Always present, even when the model performs minimal reasoning. |
| `summary` | ❌ No | An array of content (text and/or images) summarizing the reasoning. May be empty depending on the [`thinking_summaries`](https://ai.google.dev/api/interactions-api) config, whether the model performed enough reasoning, or the content type (for example, image latents may not have text summaries). |
**Note:** The Interactions API handles thoughts and signatures differently than the `generateContent` API: - In the `generateContent` API, there are no dedicated thought blocks. Because of this, signatures are metadata that can be attached to any part, such as living inside `functionCall` parts or the final part of a response. - In the Interactions API, thoughts are a first-class representation as dedicated `thought` steps.

...

## Interactions with thinking
```
import { GoogleGenAI } from "@google/genai" ; const client = new GoogleGenAI ({}); const interaction = await client . interactions . create ({ model : "gemini-3.8-flash" , input : "Explain the concept of Occam's Razor and provide a simple, everyday example." }); console . log ( interaction . output_text );
```
```
import com.google.genai.Client ; import com.google.genai.gaos.models.interactions.CreateModelInteraction ; import com.google.genai.gaos.models.interactions.Interaction ; import com.google.genai.gaos.models.interactions.InteractionsInput ; import com.google.genai.gaos.models.interactions.Model ; import com.google.genai.gaos.models.operations.CreateInteractionRequestBody ; Client client = new Client (); CreateModelInteraction params = CreateModelInteraction . builder () . model ( Model . of ( "gemini-3.8-flash" )) . input ( InteractionsInput . of ( "Explain the concept of Occam's Razor and provide a simple, everyday example." )) . build (); Interaction interaction = client . interactions . create ( CreateInteractionRequestBody . of ( params )). interaction (). get (); System . out . println ( interaction . outputText (). orElse ( "" ));
```
```
package main import ( "context" "fmt" "log" "google.golang.org/genai" "google.golang.org/genai/interactions/models/interactions" "google.golang.org/genai/interactions/models/operations" ) func main () { ctx := context . Background () client , err := genai . NewClient ( ctx , nil ) if err != nil { log . Fatal ( err ) } res , err := client . Interactions . Create ( ctx , operations . CreateInteractionRequest { Body : operations . NewCreateInteractionRequestBody ( interactions . CreateModelInteraction { Model : interactions . Model ( "gemini-3.8-flash" ), Input : interactions . NewInteractionsInput ( "Explain the concept of Occam's Razor and provide a simple, everyday example." ), }), }) if err != nil { log . Fatal ( err ) } if res . Interaction . OutputText != nil { fmt . Println ( * res . Interaction . OutputText ) } }
```
```
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \ -H "x-goog-api-key:  $GEMINI_API_KEY " \ -H 'Content-Type: application/json' \ -d '{     "model": "gemini-3.8-flash",     "input": "Explain the concept of Occam' \' 's Razor and provide a simple example."   }'
```

## Thought summaries
Thought summaries provide insights into the model's internal reasoning process.
By default, only the final output is returned. You can enable thought summaries
with `thinking_summaries` :
Python JavaScript Java Go REST
```
from google import genai client = genai . Client () interaction = client . interactions . create ( model = "gemini-3.8-flash" , input = "What is the sum of the first 50 prime numbers?" , generation_config = { "thinking_summaries" : "auto" } ) for step in interaction . steps : if step . type == "thought" : print ( "Thought summary:" ) if step . summary : for content_block in step . summary : if content_block . type == "text" : print ( content_block . text ) print () elif step . type == "model_output" : for content_block in step . content : if content_block . type == "text" : print ( "Answer:" ) print ( content_block . text ) print ()
```
```
import { GoogleGenAI } from "@google/genai" ; const client = new GoogleGenAI ({}); const interaction = await client . interactions . create ({ model : "gemini-3.8-flash" , input : "What is the sum of the first 50 prime numbers?" , generation_config : { thinking_summaries : "auto" } }); for ( const step of interaction . steps ) { if ( step . type === "thought" ) { console . log ( "Thought summary:" ); if ( step . summary ) { for ( const contentBlock of step . summary ) { if ( contentBlock . type === "text" ) console . log ( contentBlock . text ); } } } else if ( step . type === "model_output" ) { for ( const contentBlock of step . content ) { if ( contentBlock . type === "text" ) { console . log ( "Answer:" ); console . log ( contentBlock . text ); } } } }
```
```
import com.google.genai.Client ; import com.google.genai.gaos.models.interactions.Content ; import com.google.genai.gaos.models.interactions.CreateModelInteraction ; import com.google.genai.gaos.models.interactions.GenerationConfig ; import com.google.genai.gaos.models.interactions.Interaction ; import com.google.genai.gaos.models.interactions.InteractionsInput ; import com.google.genai.gaos.models.interactions.Model ; import com.google.genai.gaos.models.interactions.ModelOutputStep ; import com.google.genai.gaos.models.interactions.Step ; import com.google.genai.gaos.models.interactions.TextContent ; import com.google.genai.gaos.models.interactions.ThinkingSummaries ; import com.google.genai.gaos.models.interactions.ThoughtStep ; import com.google.genai.gaos.models.interactions.ThoughtSummaryContent ; import com.google.genai.gaos.models.operations.CreateInteractionRequestBody ; import java.util.Collections ; Client client = new Client (); CreateModel
```

...

```
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \ -H "x-goog-api-key:  $GEMINI_API_KEY " \ -H 'Content-Type: application/json' \ -d '{     "model": "gemini-3.8-flash",     "input": "What is the sum of the first 50 prime numbers?",     "generation_config": {       "thinking_summaries": "auto"     }   }'
```

...

## Streaming with thinking
Use streaming to receive incremental thought summaries during generation.
Thought blocks are delivered using Server-Sent Events (SSE) with two distinct
delta types:
| Delta type | Contains | When sent |
| `thought_ summary` | Text or image summary content | One or more deltas with incremental summary |
| `thought_ signature` | The cryptographic signature | the last delta before `step. stop` |
Python JavaScript Java Go REST
```
from google import genai client = genai . Client () prompt = """ Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue. Alice does not live in the red house. Bob does not live in the green house. Carol does not live in the red or green house. Which house does each person live in? """ thoughts = "" answer = "" stream = client . interactions . create ( model = "gemini-3.8-flash" , input = prompt , generation_config = { "thinking_summaries" : "auto" }, stream = True ) for event in stream : if event . event_type == "step.delta" : if event . delta . type == "thought_summary" : if not thoughts : print ( "Thinking..." ) summary_text = event . delta . content . text print ( f "[Thought]  { summary_text } " , end = "" ) thoughts += summary_text elif event . delta . type == "text" and event . delta . text : if not answer : print ( " \n Answer:" ) print ( event . delta . text , end = "" ) answer += event . delta . te
```

...

```
import { GoogleGenAI } from "@google/genai" ; const client = new GoogleGenAI ({}); const prompt = `Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue. Alice does not live in the red house. Bob does not live in the green house. Carol does not live in the red or green house. Which house does each person live in?` ; let thoughts = "" ; let answer = "" ; const stream = await client . interactions . create ({ model : "gemini-3.8-flash" , input : prompt , generation_config : { thinking_summaries : "auto" }, stream : true }); for await ( const event of stream ) { if ( event . event_type === "step.delta" ) { if ( event . delta . type === "thought_summary" ) { if ( ! thoughts ) console . log ( "Thinking..." ); const text = event . delta . content ? . text || "" ; process . stdout . write ( `[Thought]  ${ text } ` ); thoughts += text ; } else if ( event . delta . type === "text"  &&  event . delta . text ) { if (
```

...

```
ionRequestBody ; import com.google.genai.gaos.models.operations.CreateInteractionResponse ; import com.google.genai.gaos.utils.EventStream ; Client client = new Client (); String prompt = "Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.\n" + "Alice does not live in the red house.\n" + "Bob does not live in the green house.\n" + "Carol does not live in the red or green house.\n" + "Which house does each person live in?" ; StringBuilder thoughts = new StringBuilder (); StringBuilder answer = new StringBuilder (); CreateModelInteraction params = CreateModelInteraction . builder () . model ( Model . of ( "gemini-3.8-flash" )) . input ( InteractionsInput . of ( prompt )) . generationConfig ( GenerationConfig . builder (). thinkingSummaries ( ThinkingSummaries . AUTO ). build ()) . stream ( true ) . build (); CreateInteractionResponse response = client . interactions . create ( CreateInteractionRequestBod
y . of ( params )); try ( EventStream<InteractionSSEStreamEvent> stream = response . events ()) { for ( InteractionSSEStreamEvent streamEvent : stream ) { InteractionSSEEvent event = streamEvent . data (). orElse ( null ); if ( event instanceof StepDelta stepDelta ) { StepDeltaData delta = stepDelta . delta (). orElse ( null ); if ( delta instanceof ThoughtSummaryDelta thoughtDelta ) { Content content = thoughtDelta . content (). orElse ( null ); if ( content instanceof TextContent textContent ) { if ( thoughts . length () == 0 ) { System . out . println ( "Thinking..." ); } String summaryText = textContent . text (). orElse ( "" ); System . out . print ( "[Thought] " + summaryText ); thoughts . append ( summaryText ); } } else if ( delta instanceof TextDelta textDelta ) { String text = textDelta . text (). orElse ( "" ); if ( ! text . isEmpty ()) { if ( answer . length () == 0 ) { System . out . println ( "\nAnswer:" ); } System . out . print (
```

...

```
:= step . ThoughtStep ; thought != nil { for _ , part := range thought . Summary { if part . TextContent != nil { fmt . Printf ( "Thought summary:\n%s\n\n" , part . TextContent . Text ) } } } } if res . Interaction . OutputText != nil { fmt . Printf ( "Answer:\n%s\n" , * res . Interaction . OutputText ) } }
```
```
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \ -H "x-goog-api-key:  $GEMINI_API_KEY " \ -H 'Content-Type: application/json' \ --no-buffer \ -d '{     "model": "gemini-3.8-flash",     "input": "Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue. Alice does not live in the red house. Bob does not live in the green house. Carol does not live in the red or green house. Which house does each person live in?",     "generation_config": {       "thinking_summaries": "auto"     },     "stream": true   }'
```

...

```
event: interaction.created
data: {"interaction":{"id":"v1_xxx","status":"in_progress","object":"interaction","model":"gemini-3.8-flash"},"event_type":"interaction.created"}

event: step.start
data: {"index":0,"step":{"signature":"","summary":[{"text":"**Evaluating the clues**\n\nI'm considering...","type":"text"}],"type":"thought"},"event_type":"step.start"}

event: step.delta
data: {"index":0,"delta":{"signature":"EpoGCpcGAXLI2nx/...","type":"thought_signature"},"event_type":"step.delta"}

event: step.stop
data: {"index":0,"event_type":"step.stop"}

event: step.start
data: {"index":1,"step":{"content":[{"text":"Based on the clues provided, here","type":"text"}],"type":"model_output"},"event_type":"step.start"}

event: step.delta
data: {"index":1,"delta":{"text":" is the answer to your question...","type":"text"},"event_type":"step.delta"}

event: step.stop
data: {"index":1,"event_type":"step.stop"}

event: interaction.completed
data: {"interaction":{"id":"v1_xxx","status":"completed","usage":{"total_tokens":530,"total_input_tokens":62,"total_output_tokens":171,"total_thought_tokens":297}},"event_type":"interaction.completed"}

event: done
data: [DONE]
```

## Controlling thinking
Gemini models engage in dynamic thinking by default, automatically adjusting
the amount of reasoning effort based on the complexity of the request. You can control this behavior using the `thinking_level` parameter.

...

```
from google import genai client = genai . Client () interaction = client . interactions . create ( model = "gemini-3.8-flash" , input = "Provide a list of 3 famous physicists and their key contributions" , generation_config = { "thinking_level" : "low" } ) print ( interaction . output_text )
```
```
import { GoogleGenAI } from "@google/genai" ; const client = new GoogleGenAI ({}); const interaction = await client . interactions . create ({ model : "gemini-3.8-flash" , input : "Provide a list of 3 famous physicists and their key contributions" , generation_config : { thinking_level : "low" } }); console . log ( interaction . output_text );
```
```
import com.google.genai.Client ; import com.google.genai.gaos.models.interactions.CreateModelInteraction ; import com.google.genai.gaos.models.interactions.GenerationConfig ; import com.google.genai.gaos.models.interactions.Interaction ; import com.google.genai.gaos.models.interactions.InteractionsInput ; import com.google.genai.gaos.models.interactions.Model ; import com.google.genai.gaos.models.interactions.ThinkingLevel ; import com.google.genai.gaos.models.operations.CreateInteractionRequestBody ; Client client = new Client (); CreateModelInteraction params = CreateModelInteraction . builder () . model ( Model . of ( "gemini-3.8-flash" )) . input ( InteractionsInput . of ( "Provide a list of 3 famous physicists and their key contributions" )) . generationConfig ( GenerationConfig . builder (). thinkingLevel ( ThinkingLevel . LOW ). build ()) . build (); Interaction interaction = client . interactions . create ( CreateInteractionRequestBody . of
```

...

```
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \ -H "x-goog-api-key:  $GEMINI_API_KEY " \ -H 'Content-Type: application/json' \ -d '{     "model": "gemini-3.8-flash",     "input": "Provide a list of 3 famous physicists and their key contributions",     "generation_config": {       "thinking_level": "low"     }   }'
```

...

### Token limits and `max_ output_ tokens`
* **Long decode (up to 1M tokens):** To allow Gemini 4 to reason and generate beyond `65,536` tokens (up to `1,048,576` tokens), set `background=True` and configure `max_output_tokens` greater than `65,536` . See [Long decode](https://ai.google.dev/gemini-api/docs/long-decode) for details.

## Thought signatures
Thought signatures are encrypted representations of the model's internal reasoning. They are required to maintain reasoning continuity across multi-turn interactions.
The Interactions API makes handling thought signatures much simpler than the `generateContent` API.

...

## Pricing
Thinking models generate full thoughts to improve the quality of the final
response, and then output summaries to provide insight into the
thought process. Pricing is based on the full thought tokens the model needs to
generate, despite only the summary being output from the API.
**Note:** Because `max_output_tokens` applies to the combined total of thinking tokens and output tokens, setting a low limit can truncate responses. See Token limits and `max_output_tokens` for details.

...

## Best practices
* **Review reasoning** : Analyze thought summaries to understand failures and improve prompts.
* **Control thinking budget** : Prompt the model to think less for lengthy outputs to save tokens.
* **Simple tasks** : Use minimal or low thinking for fact retrieval or classification (e.g., "Where was DeepMind founded?").
* **Moderate tasks** : Use default thinking for comparing concepts or creative reasoning (e.g., Compare electric and hybrid cars).
* **Complex tasks** : Use maximum thinking for advanced coding, math, or multi-step planning (e.g., Solve AIME math problems).

## What's next
* [Text generation](https://ai.google.dev/gemini-api/docs/text-generation) : Basic text responses
* [Function calling](https://ai.google.dev/gemini-api/docs/function-calling) : Connect to tools
* [Gemini 4 guide](https://ai.google.dev/gemini-api/docs/latest-model) : What's new in Gemini 4
* [Gemini 3 guide](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.8) : Model-specific
  features

...

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0) . For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.