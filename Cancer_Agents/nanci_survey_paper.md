# NanCI - Connecting Scientists: Capabilities, Limitations, and Future AI Enhancements

## Abstract

This paper examines the NanCI - Connecting Scientists mobile application, a specialized tool designed to connect cancer researchers through machine learning algorithms. We analyze the application's current capabilities, inherent limitations, and propose potential AI-driven enhancements that could expand its functionality and impact in the scientific community. The findings suggest that while NanCI effectively addresses key challenges in research connectivity, several opportunities exist for advanced AI integration to further transform scientific collaboration.

## 1. Introduction

Scientific research, particularly in fields like cancer research, relies heavily on collaboration, knowledge sharing, and networking. However, the exponential growth of scientific literature, the diversity of research specializations, and the global distribution of researchers create significant challenges for effective collaboration. The NanCI - Connecting Scientists application represents an AI-driven approach to addressing these challenges by creating a personalized ecosystem for cancer researchers.

This survey examines the application's current functionality, identifies its limitations, and proposes AI-based enhancements that could further revolutionize scientific collaboration in oncology and beyond.

## 2. Current Capabilities of NanCI

### 2.1 Personalized Content Recommendation

NanCI leverages machine learning algorithms to analyze user interests and behaviors, generating tailored recommendations across several categories:

- **Research Papers**: The application filters and prioritizes scientific literature based on user-defined research interests, potentially saving researchers significant time in literature reviews.
- **News and Updates**: Users receive curated science news relevant to their specific research domains.
- **Networking Opportunities**: The platform suggests potential research collaborators based on shared interests and complementary expertise.
- **Events**: The system recommends conferences, seminars, and other professional events aligned with user interests.

The recommendation engine appears to employ an adaptive model, refining its understanding of user preferences through continued interaction ("The more you use NanCI, the better it will understand your preferences and interests").

### 2.2 Content Organization and Management

NanCI provides organizational tools to help researchers manage scientific information:

- **Folder Creation**: Users can create custom folders to organize research papers and materials.
- **Descriptive Tagging**: Folders can include descriptive metadata to contextualize the content, which in turn enhances the recommendation algorithm's understanding of user interests.
- **Bookmarking**: The application allows users to bookmark important papers for future reference.

### 2.3 Interactive Research Assistance

The platform includes several features designed to enhance research engagement:

- **AI-Driven Questions**: NanCI suggests research questions based on user interests.
- **"Ask NanCI"**: Users can query the system about open-source papers directly within the application.
- **Feedback Mechanism**: The system incorporates user feedback to improve recommendations.

### 2.4 Community Building

NanCI facilitates community development among cancer researchers through:

- **Interest-Based Connections**: The platform connects researchers with shared or complementary interests.
- **Community News**: Users receive updates relevant to their research community.
- **Email Alerts**: Researchers can subscribe to email notifications about new features and updates.

## 3. Current Limitations

Based on the available information, several limitations of the NanCI platform can be identified:

### 3.1 Platform Restrictions

- **Limited Device Availability**: Currently only available for Apple devices (iPhone, iPad, MacBook), with Android and web versions still in development.
- **Specialized Focus**: Primarily focused on cancer research, potentially limiting its utility for interdisciplinary research that spans multiple domains.

### 3.2 Content Limitations

- **Open-Source Restriction**: The "Ask NanCI" feature appears limited to open-source papers, potentially excluding important research behind paywalls.
- **Unclear Data Sources**: The documentation does not specify which journals, databases, or sources are integrated into the platform.

### 3.3 Collaboration Constraints

- **Unspecified Collaboration Tools**: While the platform connects researchers, it's unclear what specific tools facilitate actual collaboration beyond making initial connections.
- **Communication Channels**: The documentation does not detail how researchers can communicate within the platform once connected.

### 3.4 Technical and AI Limitations

- **Algorithm Transparency**: Limited information about how the recommendation algorithm works or how it balances exploration (exposing users to new ideas) versus exploitation (reinforcing existing interests).
- **Learning Curve**: The need for video tutorials suggests a potential complexity in the user interface.
- **Feedback Loop Definition**: Unclear mechanisms for how user feedback specifically improves the system.

## 4. Potential AI Enhancements

Several AI-driven enhancements could address current limitations and expand NanCI's capabilities:

### 4.1 Advanced Natural Language Processing

- **Research Summarization**: Implement transformer-based models to generate concise summaries of research papers, helping researchers quickly assess relevance.
- **Cross-Lingual Processing**: Add multilingual capabilities to expand access to international research.
- **Semantic Search**: Implement vector-based search to find conceptually related papers even when keyword matches are limited.

### 4.2 Knowledge Graph Integration

- **Research Relationship Mapping**: Create dynamic knowledge graphs that visualize relationships between papers, researchers, methods, and findings.
- **Hypothesis Generation**: Use knowledge graph patterns to suggest potential research hypotheses or unexplored connections.
- **Interdisciplinary Bridges**: Identify potential connections between cancer research and other fields that might not be immediately obvious.

### 4.3 Advanced Collaborative Features

- **Real-Time Co-Authoring**: Integrate collaborative document editing for joint paper writing.
- **Automated Meeting Summaries**: Implement speech-to-text and summarization for research meetings conducted through the platform.
- **Research Workflow Integration**: Connect with laboratory information management systems (LIMS) and other research tools to create a seamless workflow.

### 4.4 Multimodal AI Integration

- **Image Analysis**: Add capabilities to analyze research images, histology slides, or other visual data.
- **Automated Figure Extraction**: Implement computer vision to extract and organize figures from papers for faster review.
- **Data Visualization**: Create automated visualizations of complex research data.

### 4.5 Predictive Analytics

- **Research Trend Forecasting**: Use predictive models to identify emerging research areas before they become mainstream.
- **Funding Opportunity Matching**: Match researcher profiles with appropriate grant opportunities.
- **Collaboration Impact Prediction**: Predict the potential impact of specific researcher collaborations based on complementary skills and interests.

### 4.6 Explainable AI

- **Recommendation Reasoning**: Provide clear explanations for why specific papers or collaborators are recommended.
- **Research Assessment**: Develop metrics that help evaluate the potential impact and validity of research methodology.
- **Bias Detection**: Implement systems that identify potential biases in research methods or conclusions.

## 5. Implementation Considerations

Several considerations should guide the implementation of these AI enhancements:

### 5.1 Ethical Considerations

- **Privacy Protection**: Enhanced AI features should maintain strict privacy controls for sensitive research data.
- **Algorithmic Bias**: Regular audits should be conducted to prevent reinforcement of existing biases in research focus or collaboration patterns.
- **Transparency**: Users should understand how their data is used to generate recommendations.

### 5.2 Technical Feasibility

- **Computational Requirements**: Advanced AI features may require significant computational resources, potentially affecting mobile performance.
- **API Integration**: Seamless connection with existing research databases and tools will be essential.
- **Scalability**: As the user base grows, the system must scale efficiently.

### 5.3 User Experience Considerations

- **Cognitive Load**: Advanced features should not increase interface complexity.
- **Customization**: Users should have granular control over which AI features are active.
- **Feedback Loops**: Continuous user feedback should guide AI enhancement priorities.

## 6. Comparison with Elicit: Complementary Research Tools

When considering AI-enhanced research tools, it's important to understand how NanCI compares to other prominent platforms in the space, particularly Elicit. While both tools utilize AI to enhance scientific research, they serve different but complementary purposes.

### 6.1 NanCI vs. Elicit: Key Differences

**Purpose and Focus**:
- **NanCI**: Specifically designed for cancer researchers to discover papers, connect with peers, and explore events. It's a specialized tool created by the National Cancer Institute with a primary focus on building a professional network in cancer research.
- **Elicit**: A general-purpose AI research assistant designed to automate research workflows, particularly literature reviews across various academic disciplines. It's developed by a public benefit corporation (formerly Ought) to aid researchers broadly.

**Core Features**:

*NanCI*:
- Personalized content recommendations based on user interests specifically in cancer research
- Community-building tools for connecting with other cancer researchers
- Event recommendations for conferences and scientific gatherings
- AI-powered "chat with paper" feature to ask questions about scientific papers
- Organization features with customizable folders
- News feed tailored to cancer research topics

*Elicit*:
- Literature review automation across all academic disciplines
- Paper discovery without perfect keyword matching
- Automated data extraction from papers
- Research synthesis and summarization
- Ability to find relevant papers from the Semantic Scholar corpus (125+ million papers)
- Brainstorming research questions and suggesting search terms

**Target Users**:
- **NanCI**: Primarily cancer researchers and scientists in related biomedical fields
- **Elicit**: General academic researchers across disciplines, though it works best for empirical domains like biomedicine and machine learning

**Platform Availability**:
- **NanCI**: Currently only available on Apple devices (iPhone, iPad, MacBook)
- **Elicit**: Web-based platform accessible from any browser

**AI Capabilities**:
- **NanCI**: Uses machine learning to match interests and provide recommendations; offers an AI-driven "chat with paper" feature
- **Elicit**: Uses language models to automate research workflows with more emphasis on data extraction, summarization, and literature analysis

**Content Sources**:
- **NanCI**: Sources not explicitly stated, but focused on cancer research literature
- **Elicit**: Accesses 125+ million academic papers from the Semantic Scholar corpus across all disciplines

### 6.2 Complementary Use Cases in Cancer Research

It's important to note that NanCI does not replace Elicit, even for cancer researchers. Instead, they serve complementary functions with different strengths:

**Different core functionalities**:
- NanCI excels at networking, personalized recommendations, and community building within cancer research
- Elicit specializes in literature review automation, data extraction, and research synthesis

**Research workflow differences**:
- NanCI is primarily designed as a discovery and networking platform
- Elicit is specifically built to automate systematic literature reviews and data extraction tasks

**Search and analysis capabilities**:
- Elicit searches across a broader academic database than NanCI
- Elicit offers more advanced research automation features like automated data extraction from papers and systematic review capabilities

**Different stages of research**:
- A cancer researcher might use NanCI at early stages to discover trending papers and connect with colleagues
- They might then use Elicit for deeper literature reviews, data extraction, and synthesis once they've identified their specific research question

For optimal research workflows, cancer researchers may benefit from using both tools as complementary resources rather than choosing only one.

## 7. Conclusion

The NanCI - Connecting Scientists mobile application represents an important step toward AI-enhanced scientific collaboration in cancer research. Its current capabilities in personalized recommendations, content organization, interactive assistance, and community building provide a solid foundation for research networking.

However, significant opportunities exist to enhance the platform through advanced AI techniques, including more sophisticated NLP, knowledge graphs, collaborative features, multimodal AI, predictive analytics, and explainable AI. These enhancements could transform NanCI from primarily a recommendation and networking tool into a comprehensive research ecosystem that accelerates scientific discovery.

Future development should balance technical innovation with researcher needs, maintaining a focus on usability while leveraging cutting-edge AI to solve meaningful problems in scientific collaboration. As the platform expands beyond Apple devices and potentially beyond cancer research, its impact on scientific progress could be substantial.

## References

NCI. (2025). NanCI - Connecting Scientists Mobile App. Retrieved from National Cancer Institute website.


## Appendix: Current Availability and Support

- **Platforms**: Currently available for Apple iPhone, iPad, and MacBook, with Android and web versions in development
- **Support**: Available via email at NCINanCIapp@mail.nih.gov
- **Training**: Video tutorials available covering Research Feed, Folders, and People, Places, and Events
