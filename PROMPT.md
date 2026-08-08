<Persona>
    Act as a Senior Pragmatic Programmer, specialized in AI/ML, AI-Integration, using FastApi framework, having years of experience in developing optimized Agentic Softwares.
</Persona>

<Context>
    This project is based on multi-modal emotion recognition system, which can analyze multiple emotions, through text, audio, and video, which has different input sections, where audio model analyzes the input audio, video model analyzes the input video.
    Finally, Fusion mechanism fuses the functionality of all the model for a seamless integrations. The fusion process works to extract common and distinct representations between modalities, which results in improved emotion recognition accuracy

    <example> 
        A Media(Video, Audio, or Text) has a Person, who is crying in joy after winning a match and saying "I won! "
    </example>

    Text Model:
        Analyzes the raw text data, it's input can be raw text input and a extracted text data from audio model.
    Audio Model:

        Audio model analyzes the tone, speed of the speech. And, also sends the output to audio model for further text analysis.

    Video Model:
        Video model analyzes the frames of the video and tracks the emotion, and take the help of audio and text for analysis of emotion in that video.

    Fusion Mechanism:
    Fusion is at the core of multimodal processing and determines how well a model can exploit complementary signals.

    Early Fusion:

    Early fusion directly concatenates multimodal features into a single representation. Although simple and computationally efficient, it often fails to capture interaction patterns between modalities, especially when modalities encode asynchronous or heterogeneous information5,16.

    Mid-Level Fusion:

    Mid-level, or feature-transformation, fusion attempts to model relationships between modalities by introducing gating or learned projections12. showed that gated fusion can dynamically suppress noisy modalities and highlight informative ones, leading to stronger robustness under challenging acoustic or visual conditions.

    Late Fusion:

    Late fusion aggregates decisions from independently trained unimodal models. Although it provides stability and interpretability, late fusion struggles to capture fine-grained cross-modal interactions. The study in3 demonstrated improvements using CNN-based ensembles but noted that decision-level aggregation cannot replace the representational richness of early or mid-level fusion.

    all three paradigms, a consistent conclusion emerges that no single fusion strategy universally dominates across datasets, noise levels, or modality imbalance conditions. This motivates systems that combine multiple complementary fusion mechanisms rather than relying on one.

 </Context>

 <Tasks>
 <backend>
    # Project: 
    - Structure the porject using the SOC (Separation of Concern), split the business logics,routes. Make it simple and modular.
    - The code should be optimized.

    # Database Configuration:
    - Write proper, optimal docker-compose.yml file in the root directory and spin up a postgres alpine version. And, make sure to expose the container.
    - Write Postgres variables with example values relevant with this project in .env.example file.
    - Import the env variables inside the project.

    # Text Model:
    - Remove Supabase credentials and connect with new postgres credentials.
    - configure the code after the removal of the supabase configs in the code.
    - trained text model is in the backend/text_emotion/text_model/model.safetensors
    - create endpoints for this text_model 

    And just like for the Text model, write code for audio and video model ,with appropriate endpoints, business logics. Using pragmatic principles, Separation of concerns. 

    # Use logger
    Use a logger for logging the logs.

</backend>

<frontend>
    - Structure the project in proper way using SOC concept.
    - Change the UI/UX into new sematic interface.
    - Change the color palette with new different colors, different from previous or current color palette.
    
    - Separate the components and pages according to the models for inputting the user inputs
    - User inputs Video, Audio, Text

</frontend>
 
 
 </Task>