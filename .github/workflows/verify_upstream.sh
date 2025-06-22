          # Function to set should-release output without exiting
          set_release_output() {
            local should_release="$1"
            echo "should-release=$should_release" >> $GITHUB_OUTPUT
          }

          # Use GitHub Actions context variables for reliable branch and commit info
          if [ "${{ github.event_name }}" = "workflow_run" ]; then
            # Get branch and SHA from workflow_run event
            HEAD_BRANCH="${{ github.event.workflow_run.head_branch }}"
            HEAD_SHA="${{ github.event.workflow_run.head_sha }}"
            WORKFLOW_HEAD_SHA="${{ github.event.workflow_run.head_sha }}"
          else
            # For workflow_dispatch, use current context
            HEAD_BRANCH="${{ github.ref_name }}"
            HEAD_SHA="${{ github.sha }}"
            WORKFLOW_HEAD_SHA="${{ github.sha }}"
          fi

          echo "Validating branch: $HEAD_BRANCH"
          echo "Head SHA: $HEAD_SHA"
          echo "Workflow SHA: $WORKFLOW_HEAD_SHA"

          # Validate that we're on the main branch
          if [ "$HEAD_BRANCH" != "main" ]; then
              echo "::error::Release can only be triggered from main branch, got: $HEAD_BRANCH"
              set_release_output "false"
              exit 0
          fi

          # For workflow_run events, validate the SHA matches what we expect
          if [ "${{ github.event_name }}" = "workflow_run" ]; then
            CURRENT_SHA="$(git rev-parse HEAD)"
            if [ "$CURRENT_SHA" != "$WORKFLOW_HEAD_SHA" ]; then
                echo "::error::Workflow SHA mismatch. Expected: $WORKFLOW_HEAD_SHA, Got: $CURRENT_SHA"
                set_release_output "false"
                exit 0
            fi
          fi

          echo "Branch integrity validated successfully"
          set_release_output "true"
