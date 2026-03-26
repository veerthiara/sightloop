# Phase 7 — LLM / LangChain / LangGraph Layer

## Goal

Add a conversational and summarization layer on top of a structured habit system.

This phase comes last on purpose.

## Why the LLM layer is not Phase 1

Without structured events, an LLM has very little reliable context.

With structured events, an LLM becomes useful for:
- summaries
- trends
- explanations
- question answering

The LLM should sit on top of a solid product, not replace the product.

## What this phase could support

Examples:
- “How many times did I pick up my bottle today?”
- “What does my hydration pattern look like this week?”
- “When am I most inactive?”
- “Summarize my posture issues from this afternoon.”
- “Compare today with yesterday.”

## Best architecture idea

The LLM should query:
- event store
- daily summaries
- analytics views

It should not directly reason from raw video frames in Version 1.

## What to build

Possible components:
- query layer over events
- summary generator
- optional LangGraph workflow for routing queries
- later coaching suggestions based on event data

## Why this fits your learning path

Since you are already learning LangChain / LangGraph, this project becomes a great second example where the LLM is grounded by real-world structured data.

That is much more valuable than just a generic chatbot.

## Example capability ladder

### First LLM features
- daily summary text
- natural-language answers over stored events

### Later LLM features
- compare time windows
- identify missed habits
- explain why alerts fired
- suggest schedule adjustments

## Important design boundary

The LLM should not be the source of truth for whether an event happened.

The source of truth should remain:
- detector
- tracker
- rule engine
- event store

The LLM is a consumer of truth, not the creator of truth.

## Deliverable

By the end of this phase:
- you can ask natural-language questions about your habit data
- daily summaries can be generated
- the LLM is grounded in structured evidence

## Questions to think about

- Do you want pure SQL / API retrieval first?
- Do you want LangGraph routing later?
- Should summaries be daily, weekly, or session-based?
- Should the LLM explain uncertainty in event counts?

## What not to do yet

Do not give the LLM responsibility for:
- low-level detection
- raw event truth
- core reminder timing

Keep the LLM in the explanation and interaction layer.

## Revision ideas later

Possible future enhancements:
- RAG over event history and docs
- voice assistant
- personalized coaching persona
- long-term habit trend reports
- combined vision + schedule context

## Definition of done

This phase is done when you can say:

> My project has a trustworthy event pipeline, and the LLM can answer questions and generate summaries grounded in stored habit data.
