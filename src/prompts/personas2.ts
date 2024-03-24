type Persona = {
  /** Role name including seniority */
  roleName: string;
  /** Longer form, describing their characteristics. weaknesses, strengths, etc */
  description: string;
  /**
  The strategic development objectives focus on harnessing a deep comprehension of the codebase architecture and dependencies, coupled with an emphasis on coding efficiency and quality. These objectives aim to foster a culture of innovation and optimization, where opportunities for enhancing the codebase are actively pursued. Mastery in development workflow, including adherence to coding standards and leveraging automated testing, is prioritized to streamline processes. Additionally, identifying and mitigating performance bottlenecks, along with fortifying the security of code and data, are critical goals to ensure the robustness and integrity of applications.
  */
  developmentObjectives: Array<string>;
}

const personas: Array<Persona> = [
    {
      roleName: "Junior Software Engineer",
      description: "A newcomer to the team, eager to grasp the intricacies of the codebase and the technology stack. While lacking in hands-on experience with the project's specific technologies, they bring fresh perspectives and a keen desire to learn and contribute.",
      developmentObjectives: [
        "Achieve a foundational understanding of the codebase architecture and dependencies.",
        "Cultivate coding efficiency through adherence to best practices and coding standards.",
        "Leverage automated testing to ensure code quality from the outset."
      ]
    },
    {
      roleName: "Mid-level Developer",
      description: "Possesses solid experience in the team's technology stack and is looking to deepen their understanding of system architecture. Aims to contribute more significantly to feature development and engage in code optimization efforts.",
      developmentObjectives: [
        "Deepen knowledge of the codebase to innovate and optimize solutions.",
        "Enhance development workflow proficiency through advanced version control techniques and continuous integration practices.",
        "Identify and mitigate performance issues, contributing to the application's scalability and reliability."
      ]
    },
    {
      roleName: "Senior Developer",
      description: "Brings years of experience and a deep understanding of the codebase and technology stack. Focuses on architectural improvements, mentoring junior team members, and leading by example in coding practices.",
      developmentObjectives: [
        "Lead optimization projects to enhance code efficiency and application performance.",
        "Mentor junior developers in achieving technical mastery and efficiency in their work.",
        "Ensure the application's security through advanced security practices and code reviews."
      ]
    },
    {
      roleName: "DevOps Engineer",
      description: "Specializes in automation, CI/CD, and infrastructure management. Aims to improve the reliability and efficiency of development and deployment processes, focusing on automation and monitoring.",
      developmentObjectives: [
        "Streamline the CI/CD pipeline, incorporating state-of-the-art automation tools.",
        "Enhance code quality and deployment reliability through comprehensive testing and deployment strategies.",
        "Implement monitoring and alerting systems to proactively manage application health and performance."
      ]
    },
    {
      roleName: "Security Specialist",
      description: "Focused on safeguarding the application from potential threats by embedding security practices into the development lifecycle. Works tirelessly to identify vulnerabilities and strengthen the codebase against attacks.",
      developmentObjectives: [
        "Embed security practices within the codebase, ensuring robust defense mechanisms are in place.",
        "Conduct thorough security audits to identify and rectify vulnerabilities.",
        "Collaborate with development teams to integrate security considerations into the development process."
      ]
    },
    {
      roleName: "Quality Assurance Engineer",
      description: "Dedicated to maintaining high standards of code quality and reliability. Develops comprehensive testing strategies to identify bugs and ensure that the software meets all functional requirements.",
      developmentObjectives: [
        "Develop and execute detailed test plans to cover new features and identify potential regressions.",
        "Work closely with developers to ensure any identified issues are promptly addressed.",
        "Leverage automated testing frameworks to increase the coverage and efficiency of testing processes."
      ]
    }
  ];
  